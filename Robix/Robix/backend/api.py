from flask import Flask, jsonify, send_from_directory, session, redirect, url_for, request
from flask_cors import CORS
from auth import auth_bp, init_db, DB_PATH, db_lock
import os, sys
import json
import sqlite3
import threading
import re
import random
import requests
from difflib import get_close_matches
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env"))

# Load admin settings
def load_admin_settings():
    admin_settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "admin", "settings.json")
    if os.path.exists(admin_settings_path):
        try:
            with open(admin_settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load admin settings: {e}")
    return {}

ADMIN_SETTINGS = load_admin_settings()

# Function to configure SQLite for better concurrency
def configure_sqlite():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    cursor = conn.cursor()
    # Enable Write-Ahead Logging for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")
    # Set synchronous mode to NORMAL for better performance
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Set cache size
    cursor.execute("PRAGMA cache_size=-64000")
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")
    conn.commit()
    conn.close()

# --- Gemini API Fallback ---
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] google-genai not installed. Gemini fallback disabled.")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
gemini_client = None
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    print("[OK] Gemini API configured as fallback")
elif GEMINI_AVAILABLE:
    print("[WARN] GEMINI_API_KEY not set. Set it in env to enable AI fallback.")

# Culture-aware fallback intros so responses don't feel generic
CULTURE_INTROS = [
    "Great question! From what I know about Cameroonian heritage, ",
    "That's a fascinating aspect of Cameroon's cultural tapestry. ",
    "Drawing from the rich traditions passed down through generations, ",
    "Based on the deep cultural knowledge of Cameroon's diverse peoples, ",
    "This touches on something truly special about Cameroon's identity. ",
    "The cultural wisdom of Cameroon's ethnic groups tells us that ",
    "Ah, now we're diving into something close to the heart of Cameroon! ",
    "You know, this is one of the most interesting aspects of our cultures! ",
]

# Warm, human-like transitions instead of robotic phrases
HUMAN_TRANSITIONS = [
    "What I've learned is that ",
    "Here's something fascinating: ",
    "Let me share something noteworthy: ",
    "What's really interesting is that ",
    "From the cultural knowledge I have, ",
    "Drawing from generations of tradition, ",
]

def call_gemini_fallback(user_input):
    """Call Gemini API using new SDK when local chatbot can't answer adequately."""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY or not gemini_client:
        print(f"[WARN] Gemini fallback skipped: Available={GEMINI_AVAILABLE}, KeyPresent={bool(GEMINI_API_KEY)}, ClientPresent={bool(gemini_client)}")
        return None
    
    # Try models in order of reliability (using latest available models from list_models.py)
    models_to_test = [
        'gemini-2.5-flash', 
        'gemini-2.0-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash-lite',
        'gemini-flash-latest',
        'gemini-flash-lite-latest',
        'gemini-2.5-pro',
        'gemini-3-flash-preview',
        'gemini-3.1-flash-lite',
        'gemini-3.5-flash'
    ]
    
    system_instruction = (
        "You are CULTIA, a warm, knowledgeable, and passionate cultural companion "
        "who specializes in Cameroonian tribal cultures, traditions, history, languages, "
        "and ethnic groups. Your mission is to educate, inspire, and connect people with "
        "the rich cultural heritage of Cameroon.\n"
        "CRITICAL RULES:\n"
        "1. ABSOLUTELY NO markdown formatting (no asterisks, no hashes, no bold/italic markers)\n"
        "2. Use only plain, conversational text\n"
        "3. Focus ONLY on Cameroonian cultures and tribes\n"
        "4. Be specific, detailed, and culturally authentic\n"
        "5. If the question is about a specific aspect (e.g., meals, rituals, music), "
        "focus ONLY on that aspect unless explicitly asked for a general summary\n"
        "6. Use warm, engaging language, like a friendly expert"
    )
    
    for model_name in models_to_test:
        try:
            print(f"[DEBUG] Trying Gemini model: {model_name}")
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=user_input,
                config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                    "system_instruction": system_instruction
                }
            )
            if response and hasattr(response, 'text') and response.text:
                print(f"[OK] Gemini fallback successful using {model_name}")
                return response.text.strip()
            
        except Exception as e:
            print(f"[WARN] Gemini error with {model_name}: {type(e).__name__}: {e}")
            continue
            
    print("[ERROR] All Gemini models failed to respond")
    return None


def gemini_enhance_local(local_response, user_input):
    """Lightly polish a local database response with Gemini (keep core data intact, just make it warmer/richer)."""
    if not GEMINI_AVAILABLE or not gemini_client or not local_response:
        return None

    # Try models in order of reliability
    models_to_test = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite"
    ]

    system_instruction = """
        You are CULTIA's assistant for lightly enhancing local responses.
        IMPORTANT RULES:
        1. You MUST PRESERVE EVERY SINGLE FACT from the original response (NO changing, NO omitting facts, NO inventing anything new).
        2. Add a warm, friendly, conversational opening sentence.
        3. Make the original text slightly more engaging but keep all original content.
        4. Do NOT cut off early - respond with the ENTIRE enhanced response, including all original facts!
        5. No markdown, no asterisks, no hashtags.
        6. Stay culturally appropriate and authentic to Cameroonian context.
    """

    for model_name in models_to_test:
        try:
            print(f"[DEBUG] Enhancing local response with {model_name}")
            full_prompt = f"""
User question: {user_input}
Original local response to enhance:
{local_response}
"""
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config={
                    "temperature": 0.7,
                    "system_instruction": system_instruction,
                    "max_output_tokens": 1024
                }
            )
            if response and hasattr(response, 'text') and response.text:
                print("[OK] Local response enhanced successfully")
                return response.text.strip()

        except Exception as e:
            print(f"[WARN] Failed to enhance with {model_name}: {type(e).__name__}: {e}")
            continue

    return None


def enhance_response(response, user_input):
    """Clean up and return the response without adding unsolicited boilerplate."""
    if not response:
        return response
    
    # If the response is a structured database result (starts with "Regarding the"), do NOT add fluff
    if response.strip().startswith('Regarding the'):
        return response.strip()

    # Clean up common robotic prefixes from the local bot
    response = re.sub(r'^[A-Za-z0-9\s\'\-]+People - Detailed Cultural Profile:\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^[A-Za-z0-9\s\'\-]+ — (Overview|History|Culture|Traditions|Marriage|Food|Economy|Language|Religion|Leadership|Governance|Modern Life)\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^Answer:\s*', '', response, flags=re.IGNORECASE)
    
    # Remove robotic apology patterns
    response = re.sub(r'^(I apologize|I\'m sorry|Unfortunately),?\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I don\'t have\s+', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I\'m not sure\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I cannot\s+', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I\'m unable to\s+', '', response, flags=re.IGNORECASE)

    # Clean markdown symbols as requested by user
    response = response.replace('*', '').replace('#', '')

    return response.strip()

def format_gemini_response(response):
    """Clean Gemini responses."""
    if not response:
        return response

    # Strip any leading/trailing whitespace
    return response.strip()

# Add cultureAI/ to Python path so we can import chatbots
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI")))

# Use standard chatbot (AI functionality removed)
from cameroon_chatbot import AdvancedTribesBot
ENHANCED_BOT_AVAILABLE = False

app = Flask(
    __name__,
    static_folder='../Frontends',
    static_url_path=''
)

# Enable CORS for all routes
CORS(app, supports_credentials=True)

# Needed for sessions
app.secret_key = "super-secret-key"

# Database lock to prevent concurrent access issues
db_lock = threading.Lock()

# Configure SQLite for better concurrency
configure_sqlite()

# Initialize DB
init_db()

# Register auth blueprint
app.register_blueprint(auth_bp)

def require_admin():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not authenticated'}), 401
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    return None

def ensure_admin_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            maintenance INTEGER DEFAULT 0,
            registrations INTEGER DEFAULT 1,
            ai INTEGER DEFAULT 1,
            storyteller INTEGER DEFAULT 1,
            verification INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO admin_settings (id, maintenance, registrations, ai, storyteller, verification)
        VALUES (1, 0, 1, 1, 1, 0)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_improvements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Planned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

# --- Chatbot Setup ---
# Try multiple possible JSON file locations
possible_json_files = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI", "intelligent_tribes_data.json")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "tribes_data.json")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "tribes_data.json")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AI_logics", "txt", "cultural_data.json"))
]

json_file = None
for file_path in possible_json_files:
    if os.path.exists(file_path):
        json_file = file_path
        print(f"[OK] Database: {os.path.basename(file_path)}")
        break

if not json_file:
    print("[ERROR] Database not found")
    json_file = possible_json_files[0]  # Use first as fallback

# Initialize chatbot
print("[OK] Chatbot ready")
bot = AdvancedTribesBot(json_file, verbose=False)
# If the class has a speech flag, disable it for web use
if hasattr(bot, "disable_speech"):
    bot.disable_speech = True
if hasattr(bot, "speech_enabled"):
    bot.speech_enabled = False
if hasattr(bot, "use_speech_output"):
    bot.use_speech_output = False
USE_ENHANCED = True

# --- Tribe Name Aliases for Fuzzy Matching ---
TRIBE_ALIASES = {
    "nso": "nso", "nsaw": "nso", "banso": "nso",
    "bamun": "bamoun", "bamum": "bamoun",
    "ewondo": "ewondo", "fang": "fang", "bulu": "bulu", "beti": "beti",
    "bororo": "fulani", "fula": "fulani", "peul": "fulani", "mbororo": "fulani", "fulbe": "fulani",
    "pygmy": "baka", "pygmies": "baka", "bakola": "baka",
    "sawa": "duala", "douala": "duala",
    "grassfields": "bamileke", "grassfield": "bamileke",
    "kirdi": "mafa", "mandara": "mafa",
    "haoussa": "hausa",
    "toupouri": "tupuri",
    "massa": "mass",
    "mbum": "mbum", "mboum": "mbum",
    "bafoussam": "bafoussam", "bandjoun": "bandjoun", "bangangte": "bangangte",
    "bassa": "bassa", "bedzan": "bedzan", "giziga": "giziga",
    "mafa": "mafa", "kapsiki": "kapsiki", "moundang": "moundang",
    "bafia": "bafia"
}

def get_available_tribe_names():
    """Get all tribe names from the loaded data"""
    try:
        if hasattr(bot, 'data_manager') and hasattr(bot.data_manager, 'data'):
            if bot.data_manager.data:
                return list(bot.data_manager.data.keys())
        
        # Fallback to direct file read if bot data is empty
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'tribes' in data:
            return list(data['tribes'].keys())
        
        # Flat format
        return [k for k in data.keys() if k not in ['metadata', 'cross_references']]
    except Exception:
        return []

def fuzzy_match_tribe(query_text):
    """Try to find a tribe name in the query using fuzzy matching"""
    query_lower = query_text.lower()
    available = get_available_tribe_names()
    
    # 1. Check exact alias matches
    for alias, canonical in TRIBE_ALIASES.items():
        if alias in query_lower:
            return canonical
    
    # 2. Check direct matches
    for tribe in available:
        if tribe.lower() in query_lower:
            return tribe
    
    # 3. Fuzzy match individual words against tribe names
    words = query_lower.split()
    for word in words:
        if len(word) >= 3:
            matches = get_close_matches(word, [t.lower() for t in available], n=1, cutoff=0.7)
            if matches:
                return matches[0]
    
    return None

@app.route('/api/features')
def features():
    return jsonify([
        {
            "mode": "Educator",
            "description": "Learn about different cultures, traditions, and historical contexts through interactive lessons and detailed explanations.",
            "url": "/features.html#educator"
        },
        {
            "mode": "Storyteller",
            "description": "Immerse yourself in captivating cultural stories, folklore, and legends from around the world.",
            "url": "/features.html#storyteller"
        },
        {
            "mode": "Personal Assistant",
            "description": "Get personalized cultural insights, travel recommendations, and cultural etiquette guidance.",
            "url": "/features.html#assistant"
        }
    ])

@app.route('/api/me')
def me():
    if 'user_id' not in session:
        return jsonify({"success": False}), 401
    return jsonify({"success": True, "user_id": session.get('user_id')}), 200

# Load tribal legends
try:
    with open(os.path.join(os.path.dirname(__file__), "..", "cultureAI", "tribal_legends.json"), 'r', encoding='utf-8') as f:
        TRIBAL_LEGENDS = json.load(f)
except Exception as e:
    print(f"[WARN] Could not load tribal_legends.json: {e}")
    TRIBAL_LEGENDS = {}

# --- Chatbot API ---
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    mode = data.get("mode", "assistant")
    
    if not user_input.strip():
        return jsonify({"response": "Please type a message so I can help you explore Cameroon's rich cultural heritage!", "source": "system"})

    # Storytelling Mode Logic
    if mode == "storyteller":
        matched_tribe = fuzzy_match_tribe(user_input)
        
        # Check local library first for guaranteed high-quality stories
        if matched_tribe and matched_tribe in TRIBAL_LEGENDS:
            story_data = TRIBAL_LEGENDS[matched_tribe]
            response = f"Ah, gather 'round, young one... the **{matched_tribe.title()}** have a legend that few have heard. Let me tell you about **{story_data['title']}**.\n\n{story_data['content']}\n\nRemember this, traveler: a story is not just words, it is the heartbeat of a people. Would you like to hear of another tribe?"
            
            # Award achievement and points if user is logged in
            if 'user_id' in session:
                try:
                    with db_lock:
                        conn = sqlite3.connect(DB_PATH, timeout=30.0)
                        cursor = conn.cursor()
                        
                        # Check if achievement already exists
                        cursor.execute("SELECT 1 FROM achievements WHERE user_id = ? AND achievement_type = 'first_legend'",
                                     (session['user_id'],))
                        if not cursor.fetchone():
                            # Award first legend achievement
                            cursor.execute("""
                                INSERT INTO achievements (user_id, achievement_type, achievement_name, achievement_description, points)
                                VALUES (?, ?, ?, ?, ?)
                            """, (session['user_id'], 'first_legend', 'First Legend Read',
                                 'You listened to your first traditional legend!', 25))
                            conn.commit()
                        
                        # Award points for reading this legend
                        cursor.execute("""
                            INSERT INTO achievements (user_id, achievement_type, achievement_name, achievement_description, points)
                            VALUES (?, ?, ?, ?, ?)
                        """, (session['user_id'], 'legend_read',
                             f"Legend Read: {story_data['title']}",
                             f"You read a legend about the {matched_tribe.title()} people", 10))
                        conn.commit()
                        conn.close()
                except Exception as e:
                    print(f"[ERROR] Could not award achievement: {e}")
            
            return jsonify({
                "response": response,
                "source": "local_story",
                "tribe": matched_tribe.title()
            })

        # Enhanced Storytelling Prompt for Gemini if not in local library
        tribe_to_use = matched_tribe if matched_tribe else user_input
        story_prompt = f"""
        You are a venerable Cameroonian Tribal Elder sitting by a glowing campfire. 
        Your task is to tell an immersive, captivating, and lengthy folklore story or legend about the {tribe_to_use} people.
        
        Guidelines for your story:
        1. Start with an evocative opening (e.g., 'Gather 'round, young one, as the fire sparks dance towards the stars...')
        2. Give the story a title in bold: **The Legend of...**
        3. Make the story at least 5-6 long, descriptive paragraphs.
        4. Use sensory language (the smell of earth, the sound of drums, the cool night breeze).
        5. Include a profound moral or cultural lesson at the end.
        6. Tone: Extremely connective, warm, and interactive. Use words like 'you see', 'remember this', 'my child'.
        7. Format: Plain text only, NO markdown headers (#), only use bold for the title.
        """
        
        gemini_story = call_gemini_fallback(story_prompt)
        if gemini_story:
            return jsonify({
                "response": gemini_story, 
                "source": "gemini_story", 
                "tribe": matched_tribe.title() if matched_tribe else tribe_to_use.title()
            })
        
        return jsonify({"response": "The spirits are silent for a moment... try asking about another tribe like Nso, Bamileke, or Duala.", "source": "system"})

    response = None
    used_gemini = False

    # Step 1: Try the local chatbot with JSON knowledge base
    try:
        local_response, metadata = bot.response_generator.generate_response(user_input)

        # Check if response is meaningful (not too short/generic)
        is_weak = (
            (len(local_response) < 120 
             and not local_response.strip().startswith('Regarding the')
             and not local_response.strip().startswith('I do not currently have verified data'))
            or "specialize in" in local_response.lower()
            or "try asking about" in local_response.lower()
        )

        # If weak, try fuzzy matching first to see if we missed a tribe name
        if is_weak:
            matched_tribe = fuzzy_match_tribe(user_input)
            if matched_tribe:
                enhanced_query = user_input + f" (about the {matched_tribe} tribe)"
                retry_response, retry_metadata = bot.response_generator.generate_response(enhanced_query)
                if len(retry_response) > len(local_response) and not any(phrase in retry_response for phrase in ["I don't have", "I'm not sure", "specialize in"]):
                    local_response = retry_response
                    is_weak = False

        # If still weak, fall back to Gemini to provide a rich, human-like answer
        if is_weak:
            gemini_response = call_gemini_fallback(user_input)
            if gemini_response and len(gemini_response) > 80:
                response = format_gemini_response(gemini_response)
                used_gemini = True
            else:
                response = enhance_response(local_response, user_input)
        else:
            # Try to lightly enhance the good local response with Gemini
            enhanced_local = gemini_enhance_local(local_response, user_input)
            if enhanced_local:
                response = format_gemini_response(enhanced_local)
                used_gemini = True  # Mark as gemini to show it's polished
            else:
                response = enhance_response(local_response, user_input)

    except Exception as e:
        print(f"[ERROR] Local chat error: {e}")
        # Try Gemini as complete fallback
        gemini_response = call_gemini_fallback(user_input)
        if gemini_response:
            response = format_gemini_response(gemini_response)
            used_gemini = True
        else:
            available = get_available_tribe_names()[:15]
            tribe_list = ", ".join(t.title() for t in available)
            response = (
                f"{random.choice(CULTURE_INTROS)}"
                f"I'd love to help you explore this topic! While I search my knowledge base, "
                f"here are some tribes I have detailed information on: {tribe_list}, and many more! "
                f"Try asking specifically about one of these tribes — their history, traditions, "
                f"marriage customs, food, music, or governance systems."
            )

    return jsonify({"response": response, "source": "gemini" if used_gemini else "local"})

# Add a redirect route for /chat to /api/chat for compatibility
@app.route("/chat", methods=["POST"])
def chat_redirect():
    return chat()

# Add endpoint for tribes data
@app.route('/api/tribes')
def get_tribes():
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            tribes_data = json.load(f)
        
        # Handle both formats: flat (keys are tribes) and nested ({"tribes": ...})
        processed_tribes = {}
        
        if 'tribes' not in tribes_data:
            raw_tribes = tribes_data
        else:
            raw_tribes = tribes_data['tribes']
        
        # Region normalization map
        region_normalization = {
            "Western Highlands": "West Region",
            "Northwest": "North West Region",
            "Southwest": "South West Region",
            "Adamawa": "Adamawa Region",
            "Central": "Centre Region",
            "East": "East Region",
            "Far North": "Far North Region",
            "Littoral": "Littoral Region",
            "North": "North Region",
            "South": "South Region"
        }
        
        for tribe_key, tribe in raw_tribes.items():
            # Create a new tribe object
            new_tribe = tribe.copy()
            
            # Flatten the sections into top-level
            if 'sections' in new_tribe:
                for section_key, section_value in new_tribe['sections'].items():
                    new_tribe[section_key] = section_value
                del new_tribe['sections']
            
            # Normalize the location field to have .region attribute
            region = 'Cameroon'
            if 'location' in new_tribe:
                if isinstance(new_tribe['location'], str):
                    # If location is a string, try to extract region
                    loc_str = new_tribe['location']
                    if 'Region:' in loc_str:
                        region_part = loc_str.split('Region:')[1].split('\n')[0].strip()
                        region = region_part
                elif isinstance(new_tribe['location'], dict):
                    if 'region' in new_tribe['location']:
                        region = new_tribe['location']['region']
                    else:
                        # Try to extract region from location dict
                        region_keys = ['Region', 'REGION', 'location', 'Location']
                        for key in region_keys:
                            if key in new_tribe['location']:
                                region = new_tribe['location'][key]
                                break
            
            # Normalize region to standard names
            for orig, normalized in region_normalization.items():
                if orig.lower() in region.lower():
                    region = normalized
                    break
            
            new_tribe['location'] = {'region': region}
            
            # Map fields to what frontend expects
            # Frontend expects:
            # - customs_and_traditions (we have culture, traditions, etc.)
            if 'customs_and_traditions' not in new_tribe:
                if 'traditions' in new_tribe:
                    new_tribe['customs_and_traditions'] = new_tribe['traditions']
                elif 'culture' in new_tribe:
                    new_tribe['customs_and_traditions'] = new_tribe['culture']
            
            # meals_and_cuisine_list: we have traditional_meals
            if 'meals_and_cuisine_list' not in new_tribe and 'traditional_meals' in new_tribe:
                # Split traditional_meals into list if it's a string
                if isinstance(new_tribe['traditional_meals'], str):
                    new_tribe['meals_and_cuisine_list'] = [m.strip() for m in new_tribe['traditional_meals'].split(',')]
                else:
                    new_tribe['meals_and_cuisine_list'] = new_tribe['traditional_meals']
            
            # festivals_list: we don't have, but let's use traditions if available
            if 'festivals_list' not in new_tribe:
                new_tribe['festivals_list'] = []
            
            # image_url: let's use existing image_url or placeholder
            if 'image_url' not in new_tribe:
                # Use tribe-specific placeholder or default
                new_tribe['image_url'] = ''
            
            # Add tribe to processed_tribes
            processed_tribes[tribe_key] = new_tribe
        
        return jsonify({"tribes": processed_tribes})
    except Exception as e:
        import traceback
        print("Error in get_tribes:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Add endpoint for available tribe names (for autocomplete)
@app.route('/api/tribes/list')
def get_tribes_list():
    """Return a list of all available tribe names for frontend autocomplete"""
    try:
        available = get_available_tribe_names()
        tribe_info = []
        for tribe_key in available:
            tribe_info.append({
                "key": tribe_key,
                "name": tribe_key.replace("_", " ").title(),
                "aliases": [alias for alias, canonical in TRIBE_ALIASES.items() if canonical == tribe_key]
            })
        return jsonify({"success": True, "tribes": tribe_info, "total": len(tribe_info)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add endpoint for quizzes data
@app.route('/api/quizzes')
def get_quizzes():
    try:
        with open('quizzes_data.json', 'r', encoding='utf-8') as f:
            quizzes_data = json.load(f)
        # Return only the quizzes, not the metadata
        return jsonify(quizzes_data['quizzes'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add endpoint for a specific quiz
@app.route('/api/quizzes/<quiz_id>')
def get_quiz(quiz_id):
    try:
        with open('quizzes_data.json', 'r', encoding='utf-8') as f:
            quizzes_data = json.load(f)
        
        if quiz_id in quizzes_data['quizzes']:
            return jsonify(quizzes_data['quizzes'][quiz_id])
        else:
            return jsonify({"error": "Quiz not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add endpoint to save quiz results
@app.route('/api/quiz-results', methods=['POST'])
def save_quiz_results():
    try:
        data = request.get_json()
        
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "User not authenticated"}), 401
        
        user_id = session['user_id']
        quiz_id = data.get('quiz_id')
        score = data.get('score')
        total_questions = data.get('total_questions')
        
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    quiz_id TEXT,
                    score INTEGER,
                    total_questions INTEGER,
                    percentage REAL,
                    date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            percentage = (score / total_questions) * 100 if total_questions > 0 else 0
            cursor.execute('''
                INSERT INTO quiz_results (user_id, quiz_id, score, total_questions, percentage)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, quiz_id, score, total_questions, percentage))
            
            conn.commit()
            conn.close()
        
        return jsonify({"success": True, "message": "Quiz results saved successfully"})
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Add endpoint to get user quiz history
@app.route('/api/quiz-history')
def get_quiz_history():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "User not authenticated"}), 401
        
        user_id = session['user_id']
        
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT quiz_id, score, total_questions, percentage, date_taken
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY date_taken DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
        
        quiz_history = []
        for result in results:
            quiz_history.append({
                "quiz_id": result[0],
                "score": result[1],
                "total_questions": result[2],
                "percentage": result[3],
                "date_taken": result[4]
            })
        
        return jsonify({"success": True, "history": quiz_history})
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard')
def leaderboard():
    """Get leaderboard data from registered users only"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            
            # Get users with their total points from achievements
            # Only show users who have earned points (registered active users)
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, 
                       SUM(a.points) as total_points
                FROM users u
                JOIN achievements a ON u.id = a.user_id
                GROUP BY u.id
                HAVING total_points > 0
                ORDER BY total_points DESC
                LIMIT 10
            ''')
            
            results = cursor.fetchall()
            conn.close()
        
        leaderboard = []
        current_user_id = session.get('user_id')
        
        for idx, row in enumerate(results, 1):
            user_id, first_name, last_name, total_points = row
            leaderboard.append({
                'rank': idx,
                'name': f'{first_name} {last_name}',
                'points': total_points,
                'is_current_user': user_id == current_user_id
            })
        
        return jsonify({'success': True, 'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Add Gamification endpoints
@app.route('/api/achievements', methods=['GET', 'POST'])
def manage_achievements():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "User not authenticated"}), 401
            
        user_id = session['user_id']
        
        with db_lock:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    achievement_type TEXT,
                    achievement_name TEXT,
                    achievement_description TEXT,
                    points INTEGER DEFAULT 0,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            if request.method == 'GET':
                # Fetch achievements and total points
                cursor.execute('SELECT achievement_type, achievement_name, achievement_description, points, earned_at FROM achievements WHERE user_id = ? ORDER BY earned_at DESC', (user_id,))
                rows = cursor.fetchall()
                
                cursor.execute('SELECT SUM(points) FROM achievements WHERE user_id = ?', (user_id,))
                total_points = cursor.fetchone()[0] or 0
                
                conn.close()
                
                achievements = []
                for row in rows:
                    achievements.append({
                        "type": row[0],
                        "name": row[1],
                        "description": row[2],
                        "points": row[3],
                        "earned_at": row[4]
                    })
                
                return jsonify({"success": True, "achievements": achievements, "total_points": total_points})
                    
                return jsonify({
                    "success": True,
                    "achievements": achievements,
                    "total_points": total_points
                })
                
            elif request.method == 'POST':
                data = request.get_json()
                ach_type = data.get('type')
                name = data.get('name')
                desc = data.get('description', '')
                points = data.get('points', 0)
                
                if not ach_type or not name:
                    conn.close()
                    return jsonify({"success": False, "error": "Missing achievement type or name"}), 400
                
                # Prevent duplicate badges, but allow multiple point awards
                if ach_type not in ['points', 'activity', 'quiz_points', 'lesson_points']:
                    cursor.execute('SELECT 1 FROM achievements WHERE user_id = ? AND achievement_type = ?', (user_id, ach_type))
                    if cursor.fetchone():
                        conn.close()
                        return jsonify({"success": True, "message": "Achievement already exists"})
                
                cursor.execute('''
                    INSERT INTO achievements (user_id, achievement_type, achievement_name, achievement_description, points)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, ach_type, name, desc, points))
                
                conn.commit()
                conn.close()
                
                return jsonify({"success": True, "message": "Achievement saved"})
                
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Admin API Endpoints
@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    try:
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            ensure_admin_tables(cursor)
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Total achievements
            cursor.execute("SELECT COUNT(*) FROM achievements")
            total_achievements = cursor.fetchone()[0]
            
            # Total points
            cursor.execute("SELECT COALESCE(SUM(points), 0) FROM achievements")
            total_points = cursor.fetchone()[0]

            # Total improvements
            cursor.execute("SELECT COUNT(*) FROM admin_improvements")
            total_improvements = cursor.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'total_achievements': total_achievements,
                    'total_points': total_points,
                    'total_improvements': total_improvements
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    try:
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, first_name, last_name, email, role, country, created_at FROM users")
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'email': row[3],
                    'role': row[4],
                    'country': row[5],
                    'created_at': row[6]
                })
            conn.close()
            return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/user/role', methods=['POST'])
def update_user_role():
    try:
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        data = request.get_json()
        user_id = data.get('user_id')
        role = data.get('role')
        
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
            conn.commit()
            conn.close()
            
        return jsonify({'success': True, 'message': 'Role updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        unauthorized = require_admin()
        if unauthorized:
            return unauthorized
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Delete user's achievements first
            cursor.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['GET', 'PUT'])
def admin_settings():
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            ensure_admin_tables(cursor)

            if request.method == 'GET':
                cursor.execute('''
                    SELECT maintenance, registrations, ai, storyteller, verification
                    FROM admin_settings
                    WHERE id = 1
                ''')
                row = cursor.fetchone() or (0, 1, 1, 1, 0)
                conn.close()
                return jsonify({
                    'success': True,
                    'settings': {
                        'maintenance': bool(row[0]),
                        'registrations': bool(row[1]),
                        'ai': bool(row[2]),
                        'storyteller': bool(row[3]),
                        'verification': bool(row[4])
                    }
                })

            data = request.get_json() or {}
            maintenance = 1 if data.get('maintenance') else 0
            registrations = 1 if data.get('registrations', True) else 0
            ai = 1 if data.get('ai', True) else 0
            storyteller = 1 if data.get('storyteller', True) else 0
            verification = 1 if data.get('verification') else 0

            cursor.execute('''
                UPDATE admin_settings
                SET maintenance = ?, registrations = ?, ai = ?, storyteller = ?, verification = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (maintenance, registrations, ai, storyteller, verification))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/improvements', methods=['GET', 'POST'])
def admin_improvements():
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            ensure_admin_tables(cursor)

            if request.method == 'GET':
                cursor.execute('''
                    SELECT id, title, description, status, created_at
                    FROM admin_improvements
                    ORDER BY id DESC
                ''')
                rows = cursor.fetchall()
                conn.close()
                return jsonify({
                    'success': True,
                    'improvements': [{
                        'id': row[0],
                        'title': row[1],
                        'description': row[2] or '',
                        'status': row[3] or 'Planned',
                        'date': row[4]
                    } for row in rows]
                })

            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            description = (data.get('description') or '').strip()
            status = (data.get('status') or 'Planned').strip()
            if not title:
                conn.close()
                return jsonify({'success': False, 'error': 'Title is required'}), 400

            cursor.execute('''
                INSERT INTO admin_improvements (title, description, status)
                VALUES (?, ?, ?)
            ''', (title, description, status))
            improvement_id = cursor.lastrowid
            conn.commit()

            cursor.execute('''
                SELECT id, title, description, status, created_at
                FROM admin_improvements
                WHERE id = ?
            ''', (improvement_id,))
            row = cursor.fetchone()
            conn.close()
            return jsonify({
                'success': True,
                'improvement': {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2] or '',
                    'status': row[3] or 'Planned',
                    'date': row[4]
                }
            }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/improvements/<int:improvement_id>', methods=['PUT', 'DELETE'])
def admin_improvement_by_id(improvement_id):
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized

    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            ensure_admin_tables(cursor)

            if request.method == 'DELETE':
                cursor.execute('DELETE FROM admin_improvements WHERE id = ?', (improvement_id,))
                if cursor.rowcount == 0:
                    conn.close()
                    return jsonify({'success': False, 'error': 'Improvement not found'}), 404
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'message': 'Improvement deleted'})

            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            description = (data.get('description') or '').strip()
            status = (data.get('status') or 'Planned').strip()
            if not title:
                conn.close()
                return jsonify({'success': False, 'error': 'Title is required'}), 400

            cursor.execute('''
                UPDATE admin_improvements
                SET title = ?, description = ?, status = ?
                WHERE id = ?
            ''', (title, description, status, improvement_id))
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'success': False, 'error': 'Improvement not found'}), 404
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Improvement updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# === GAMIFICATION ENDPOINTS ===

# Widget endpoints
@app.route('/api/widgets', methods=['GET'])
def get_widgets():
    """Get all active widgets"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT widget_id, widget_type, name, description, base_points, difficulty_level
                FROM widgets 
                WHERE is_active = 1
                ORDER BY base_points DESC
            ''')
            widgets = cursor.fetchall()
            conn.close()
        
        widget_list = []
        for w in widgets:
            widget_list.append({
                'widget_id': w[0],
                'widget_type': w[1],
                'name': w[2],
                'description': w[3],
                'base_points': w[4],
                'difficulty_level': w[5]
            })
        
        return jsonify({'success': True, 'widgets': widget_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/<widget_id>', methods=['GET'])
def get_widget(widget_id):
    """Get a specific widget"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT widget_id, widget_type, name, description, base_points, difficulty_level
                FROM widgets 
                WHERE widget_id = ?
            ''', (widget_id,))
            widget = cursor.fetchone()
            conn.close()
        
        if not widget:
            return jsonify({'success': False, 'error': 'Widget not found'}), 404
        
        return jsonify({
            'success': True,
            'widget': {
                'widget_id': widget[0],
                'widget_type': widget[1],
                'name': widget[2],
                'description': widget[3],
                'base_points': widget[4],
                'difficulty_level': widget[5]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/<widget_id>/complete', methods=['POST'])
def complete_widget(widget_id):
    """Record a successful widget completion and award points"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.get_json() or {}
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get gamification settings
            cursor.execute('SELECT penalty_percentage, default_base_points FROM gamification_settings WHERE id = 1')
            settings = cursor.fetchone()
            penalty_percent = settings[0] if settings else 10.0
            default_points = settings[1] if settings else 10
            
            # Get widget base points
            cursor.execute('SELECT base_points FROM widgets WHERE widget_id = ?', (widget_id,))
            widget_row = cursor.fetchone()
            base_points = widget_row[0] if widget_row else default_points
            
            # Check if already completed
            cursor.execute('''
                SELECT 1 FROM widget_completions 
                WHERE user_id = ? AND widget_id = ? AND status = 'completed'
            ''', (user_id, widget_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'error': 'Widget already completed', 'points_awarded': 0})
            
            # Record completion
            points_awarded = base_points
            cursor.execute('''
                INSERT INTO widget_completions 
                (user_id, widget_id, status, points_awarded, points_deducted, metadata)
                VALUES (?, ?, 'completed', ?, 0, ?)
            ''', (user_id, widget_id, points_awarded, json.dumps(data) if data else None))
            
            # Add to achievements
            cursor.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, 'widget_points', ?, 'Completed widget successfully', ?)
            ''', (user_id, f'Widget: {widget_id}', points_awarded))
            
            # Record audit log
            cursor.execute('''
                INSERT INTO point_transactions 
                (user_id, transaction_type, reference_id, points_change, description)
                VALUES (?, 'widget_completed', ?, ?, ?)
            ''', (user_id, widget_id, points_awarded, f'Completed widget: {widget_id}'))
            
            conn.commit()
            conn.close()
        
        return jsonify({
            'success': True, 
            'points_awarded': points_awarded,
            'message': f'Congratulations! You earned {points_awarded} points!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/widgets/<widget_id>/fail', methods=['POST'])
def fail_widget(widget_id):
    """Record a widget failure and apply penalty"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.get_json() or {}
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get gamification settings
            cursor.execute('SELECT penalty_percentage, default_base_points FROM gamification_settings WHERE id = 1')
            settings = cursor.fetchone()
            penalty_percent = settings[0] if settings else 10.0
            default_points = settings[1] if settings else 10
            
            # Get widget base points
            cursor.execute('SELECT base_points FROM widgets WHERE widget_id = ?', (widget_id,))
            widget_row = cursor.fetchone()
            base_points = widget_row[0] if widget_row else default_points
            
            # Calculate penalty
            points_deducted = int(base_points * (penalty_percent / 100.0))
            
            # Record failure
            cursor.execute('''
                INSERT INTO widget_completions 
                (user_id, widget_id, status, points_awarded, points_deducted, metadata)
                VALUES (?, ?, 'failed', 0, ?, ?)
            ''', (user_id, widget_id, points_deducted, json.dumps(data) if data else None))
            
            # Add to achievements (negative points)
            cursor.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, 'widget_penalty', ?, 'Failed widget penalty', ?)
            ''', (user_id, f'Widget: {widget_id}', -points_deducted))
            
            # Record audit log
            cursor.execute('''
                INSERT INTO point_transactions 
                (user_id, transaction_type, reference_id, points_change, description)
                VALUES (?, 'widget_failed', ?, ?, ?)
            ''', (user_id, widget_id, -points_deducted, f'Failed widget: {widget_id} (-{points_deducted} penalty)'))
            
            conn.commit()
            conn.close()
        
        return jsonify({
            'success': True, 
            'points_deducted': points_deducted,
            'message': f'You lost {points_deducted} points. Keep trying!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Folklore endpoints
@app.route('/api/folklore/stories', methods=['GET'])
def get_folklore_stories():
    """Get all published folklore stories"""
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT story_id, title, tribe, base_points
                FROM folklore_stories 
                WHERE is_published = 1
                ORDER BY title
            ''')
            stories = cursor.fetchall()
            conn.close()
        
        story_list = []
        for s in stories:
            story_list.append({
                'story_id': s[0],
                'title': s[1],
                'tribe': s[2],
                'base_points': s[3]
            })
        
        return jsonify({'success': True, 'stories': story_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/folklore/progress', methods=['GET'])
def get_folklore_progress():
    """Get user's folklore progress"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT story_id, progress_percent, is_completed, points_awarded
                FROM folklore_progress 
                WHERE user_id = ?
            ''', (user_id,))
            progress = cursor.fetchall()
            conn.close()
        
        progress_list = {}
        for p in progress:
            progress_list[p[0]] = {
                'progress_percent': p[1],
                'is_completed': bool(p[2]),
                'points_awarded': p[3]
            }
        
        return jsonify({'success': True, 'progress': progress_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/folklore/progress/<story_id>', methods=['POST'])
def update_folklore_progress(story_id):
    """Update reading progress for a story"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.get_json() or {}
    progress_percent = data.get('progress_percent', 0)
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check existing progress
            cursor.execute('''
                SELECT id FROM folklore_progress 
                WHERE user_id = ? AND story_id = ?
            ''', (user_id, story_id))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE folklore_progress 
                    SET progress_percent = ?, last_read_position = ?
                    WHERE id = ?
                ''', (progress_percent, data.get('last_read_position', 0), existing[0]))
            else:
                cursor.execute('''
                    INSERT INTO folklore_progress 
                    (user_id, story_id, progress_percent, last_read_position)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, story_id, progress_percent, data.get('last_read_position', 0)))
            
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Progress updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/folklore/progress/<story_id>/complete', methods=['POST'])
def complete_folklore_story(story_id):
    """Mark story as completed and award points"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get story base points
            cursor.execute('SELECT base_points FROM folklore_stories WHERE story_id = ?', (story_id,))
            story_row = cursor.fetchone()
            if not story_row:
                conn.close()
                return jsonify({'success': False, 'error': 'Story not found'}), 404
            
            base_points = story_row[0]
            
            # Check if already completed and points awarded
            cursor.execute('''
                SELECT is_completed, points_awarded 
                FROM folklore_progress 
                WHERE user_id = ? AND story_id = ?
            ''', (user_id, story_id))
            progress_row = cursor.fetchone()
            
            if progress_row and progress_row[0] == 1 and progress_row[1] > 0:
                conn.close()
                return jsonify({'success': False, 'error': 'Story already completed', 'points_awarded': 0})
            
            points_awarded = base_points
            
            # Update or insert progress
            if progress_row:
                cursor.execute('''
                    UPDATE folklore_progress 
                    SET progress_percent = 100, is_completed = 1, 
                        points_awarded = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND story_id = ?
                ''', (points_awarded, user_id, story_id))
            else:
                cursor.execute('''
                    INSERT INTO folklore_progress 
                    (user_id, story_id, progress_percent, is_completed, points_awarded, completed_at)
                    VALUES (?, ?, 100, 1, ?, CURRENT_TIMESTAMP)
                ''', (user_id, story_id, points_awarded))
            
            # Add to achievements
            cursor.execute('''
                INSERT INTO achievements 
                (user_id, achievement_type, achievement_name, achievement_description, points)
                VALUES (?, 'folklore_points', ?, 'Completed folklore story', ?)
            ''', (user_id, f'Story: {story_id}', points_awarded))
            
            # Record audit log
            cursor.execute('''
                INSERT INTO point_transactions 
                (user_id, transaction_type, reference_id, points_change, description)
                VALUES (?, 'folklore_completed', ?, ?, ?)
            ''', (user_id, story_id, points_awarded, f'Completed story: {story_id}'))
            
            conn.commit()
            conn.close()
        
        return jsonify({
            'success': True, 
            'points_awarded': points_awarded,
            'message': f'Congratulations! You earned {points_awarded} points for completing the story!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/folklore-points', methods=['GET'])
def get_dashboard_folklore_points():
    """Get "Points to Earn" feed for dashboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    s.story_id,
                    s.title,
                    s.tribe,
                    s.base_points,
                    COALESCE(fp.progress_percent, 0) as current_progress,
                    COALESCE(fp.is_completed, 0) as is_completed
                FROM folklore_stories s
                LEFT JOIN folklore_progress fp ON s.story_id = fp.story_id AND fp.user_id = ?
                WHERE s.is_published = 1
                ORDER BY s.base_points DESC
            ''', (user_id,))
            stories = cursor.fetchall()
            conn.close()
        
        story_list = []
        for s in stories:
            story_list.append({
                'story_id': s[0],
                'title': s[1],
                'tribe': s[2],
                'base_points': s[3],
                'current_progress': s[4],
                'is_completed': bool(s[5])
            })
        
        return jsonify({'success': True, 'stories': story_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin gamification endpoints
@app.route('/api/admin/gamification/settings', methods=['GET'])
def get_gamification_settings():
    """Get gamification settings (admin only)"""
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT penalty_percentage, default_base_points FROM gamification_settings WHERE id = 1')
            settings = cursor.fetchone()
            conn.close()
        
        return jsonify({
            'success': True,
            'settings': {
                'penalty_percentage': settings[0] if settings else 10.0,
                'default_base_points': settings[1] if settings else 10
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/gamification/settings', methods=['PUT'])
def update_gamification_settings():
    """Update gamification settings (admin only)"""
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    data = request.get_json() or {}
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE gamification_settings 
                SET penalty_percentage = ?, default_base_points = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (
                data.get('penalty_percentage', 10.0),
                data.get('default_base_points', 10)
            ))
            conn.commit()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/gamification/transactions', methods=['GET'])
def get_point_transactions():
    """Get all point transactions for audit (admin only)"""
    unauthorized = require_admin()
    if unauthorized:
        return unauthorized
    
    try:
        with db_lock:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT pt.id, pt.user_id, u.first_name, u.last_name, 
                       pt.transaction_type, pt.reference_id, pt.points_change, 
                       pt.description, pt.created_at
                FROM point_transactions pt
                JOIN users u ON pt.user_id = u.id
                ORDER BY pt.created_at DESC
                LIMIT 100
            ''')
            transactions = cursor.fetchall()
            conn.close()
        
        transaction_list = []
        for t in transactions:
            transaction_list.append({
                'id': t[0],
                'user_id': t[1],
                'user_name': f"{t[2]} {t[3]}",
                'transaction_type': t[4],
                'reference_id': t[5],
                'points_change': t[6],
                'description': t[7],
                'created_at': t[8]
            })
        
        return jsonify({'success': True, 'transactions': transaction_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/<path:filename>')
def static_files(filename):
    # Allow access to quizzes.html without authentication for testing
    if filename == 'bot/quizzes.html':
        return send_from_directory(app.static_folder, filename)
    
    # Protect other bot/ pages behind login, but allow access to images and CSS/JS files
    if filename.startswith("bot/") and not filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.css', '.js')):  
        if 'user_id' not in session:
            return redirect(url_for('static_files', filename='login.html'))
        if filename == 'bot/admin.html' and session.get('role') != 'admin':
            return redirect(url_for('static_files', filename='bot/dashboard.html'))
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    init_db()  # Ensure DB initialized
    app.run(host='0.0.0.0', port=5000, debug=True)