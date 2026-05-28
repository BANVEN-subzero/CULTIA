from flask import Flask, jsonify, send_from_directory, session, redirect, url_for, request
from flask_cors import CORS
from auth import auth_bp, init_db
import os, sys
import json
import sqlite3
import threading
import re
import random
from difflib import get_close_matches
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env"))

# --- Gemini API Fallback ---
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] google-generativeai not installed. Gemini fallback disabled.")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
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
    """Call Gemini API when local chatbot can't answer adequately."""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        print(f"[WARN] Gemini fallback skipped: Available={GEMINI_AVAILABLE}, KeyPresent={bool(GEMINI_API_KEY)}")
        return None
    
    # Try multiple models in case one is unavailable
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = (
                "You are CULTIA, a warm, knowledgeable cultural companion specializing in Cameroonian "
                "tribal cultures, traditions, history, languages, and ethnic groups. "
                "Answer the following question with rich, specific, culturally-authentic information. "
                "CRITICAL: Do not use any markdown formatting symbols like asterisks (*) or hash symbols (#). "
                "Use plain text only. Be conversational and interactive. "
                "If the question is about a specific aspect like 'meals' or 'rituals', focus ONLY on that aspect. "
                "Do not provide a general summary unless asked for one.\n\n"
                f"Question: {user_input}"
            )
            response = model.generate_content(prompt)
            if response and response.text:
                print(f"[OK] Gemini fallback successful using {model_name}")
                return response.text.strip()
        except Exception as e:
            print(f"[WARN] Gemini fallback error with {model_name}: {e}")
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

# Register auth blueprint
app.register_blueprint(auth_bp)

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
        return jsonify({"response": "Please type a message so I can help you explore Cameroon's rich cultural heritage! 🌍", "source": "system"})

    # Storytelling Mode Logic
    if mode == "storyteller":
        matched_tribe = fuzzy_match_tribe(user_input)
        
        # Check local library first for guaranteed high-quality stories
        if matched_tribe and matched_tribe in TRIBAL_LEGENDS:
            story_data = TRIBAL_LEGENDS[matched_tribe]
            response = f"Ah, gather 'round, young one... the **{matched_tribe.title()}** have a legend that few have heard. Let me tell you about **{story_data['title']}**.\n\n{story_data['content']}\n\nRemember this, traveler: a story is not just words, it is the heartbeat of a people. Would you like to hear of another tribe?"
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
        return jsonify(tribes_data)
    except Exception as e:
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
            conn = sqlite3.connect('users.db')
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
            conn = sqlite3.connect('users.db')
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
            conn = sqlite3.connect('users.db')
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
            conn = sqlite3.connect('users.db')
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

@app.route('/<path:filename>')
def static_files(filename):
    # Allow access to quizzes.html without authentication for testing
    if filename == 'bot/quizzes.html':
        return send_from_directory(app.static_folder, filename)
    
    # Protect other bot/ pages behind login, but allow access to images and CSS/JS files
    if filename.startswith("bot/") and not filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.css', '.js')):  
        if 'user_id' not in session:
            return redirect(url_for('static_files', filename='login.html'))
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    init_db()  # Ensure DB initialized
    app.run(host='0.0.0.0', port=5000, debug=True)