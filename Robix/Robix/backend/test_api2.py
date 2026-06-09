
import sys
import os
print("=== Starting test_api2 ===")
print("CWD:", os.getcwd())

# === EXACT CODE FROM api.py lines 1-229 ===
from flask import Flask, jsonify, send_from_directory, session, redirect, url_for, request
from flask_cors import CORS
from auth import auth_bp, init_db, DB_PATH, db_lock
import json
import sqlite3
import threading
import re
import random
from difflib import get_close_matches
from dotenv import load_dotenv

print("OK: Flaks, flask_cors, auth imported okay")

# Load environment variables from .env file
print("Loading dotenv from:", os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env"))
print("OK: dotenv loaded")

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

print("OK: configure_sqlite defined")

# --- Gemini API Fallback ---
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] google-generativeai not installed. Gemini fallback disabled.")
print(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")

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
    "Here's something noteworthy: ",
    "Let me share something interesting: ",
    "What's really interesting is that ",
    "From the cultural knowledge I have, ",
    "Drawing from generations of tradition, ",
]

print("OK: Defined CULTURE_INTROS, HUMAN_TRANSITIONS")

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

print("OK: call_gemini_fallback defined")

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
    
    # Clean robotic apology patterns
    response = re.sub(r'^(I apologize|I\'m sorry|Unfortunately),?\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I don\'t have\s+', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I\'m not sure\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^I cannot\s+', '', response, flags=re.IGNORECASE)

    # Clean markdown symbols as requested by user
    response = response.replace('*', '').replace('#', '')

    return response.strip()

print("OK: enhance_response defined")

def format_gemini_response(response):
    """Clean Gemini responses."""
    if not response:
        return response

    # Strip any leading/trailing whitespace
    return response.strip()

print("OK: format_gemini_response defined")

# Add cultureAI/ to Python path so we can import chatbots
print(f"Adding to sys.path: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cultureAI'))}")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI")))
print("sys.path is now:", sys.path)

print("\n=== Attempting to import AdvancedTribesBot ===")

# Use standard chatbot (AI functionality removed)
try:
    from cameroon_chatbot import AdvancedTribesBot
    print("SUCCESS: Imported AdvancedTribesBot from cameroon_chatbot")
    ENHANCED_BOT_AVAILABLE = True
except Exception as e:
    print(f"FAILED to import AdvancedTribesBot: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())
    ENHANCED_BOT_AVAILABLE = False

print("\n=== All steps done ===")

# Now initialize the bot like api.py does!
if ENHANCED_BOT_AVAILABLE:
    print("\n=== Initializing the AdvancedTribesBot like api.py does ===")
    # Try multiple possible JSON file locations
    possible_json_files = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI", "intelligent_tribes_data.json")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "tribes_data.json")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "tribes_data.json")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AI_logics", "txt", "cultural_data.json"))
    ]
    json_file = None
    for file_path in possible_json_files:
        print(f"Checking for JSON file at {file_path}")
        if os.path.exists(file_path):
            json_file = file_path
            print(f"SUCCESS: Found JSON file at: {os.path.basename(file_path)}")
            break
    if not json_file:
        print("ERROR: No JSON file found!")
        json_file = possible_json_files[0]
    try:
        print(f"Trying to create bot with {json_file}")
        bot = AdvancedTribesBot(json_file, verbose=False)
        print("SUCCESS: AdvancedTribesBot initialized")
    except Exception as e:
        print(f"FAILED to initialize bot: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
