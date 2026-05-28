from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 🔹 Add cultureAI/ to Python path so we can import chatbots
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Try to use enhanced chatbot first, fallback to standard
try:
    from super_enhanced_chatbot import SuperEnhancedTribesBot
    ENHANCED_BOT_AVAILABLE = True
    logger.info("✅ Enhanced chatbot available")
except ImportError:
    from cameroon_chatbot import AdvancedTribesBot
    ENHANCED_BOT_AVAILABLE = False
    logger.info("⚠️ Using standard chatbot")

app = Flask(__name__)
app.secret_key = 'super_secret_cultia_key_2026_!!' # 🔑 Hardcoded for absolute session stability

# Path to JSON data
json_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI", "intelligent_tribes_data.json"))

# Register Blueprints
from auth import auth_bp
from api import api_bp
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Initialize appropriate bot
try:
    from super_enhanced_chatbot import SuperEnhancedTribesBot
    bot = SuperEnhancedTribesBot()
    USE_ENHANCED = True
    logger.info("✅ Enhanced chatbot initialized")
except ImportError:
    from cameroon_chatbot import AdvancedTribesBot
    bot = AdvancedTribesBot(json_path=json_file, verbose=False)
    USE_ENHANCED = False
    logger.info("⚠️ Using standard cameroon_chatbot")

# Root directory for bot frontend
BOT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontends", "bot"))

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data: return jsonify({"response": "⚠️ Invalid request format."}), 400
        user_input = data.get("message", "")
        if not user_input.strip(): return jsonify({"response": "⚠️ Please enter a message."}), 400

        if USE_ENHANCED:
            response = bot.chat(user_input)
        else:
            response, _ = bot.response_generator.generate_response(user_input)
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({"response": "❌ Error processing request."}), 500

@app.route("/")
def serve_index():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontends"))
    return send_from_directory(root_dir, "index.html")

@app.route("/bot/<path:filename>")
def serve_bot_files(filename):
    return send_from_directory(BOT_ROOT, filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontends", "css"))
    return send_from_directory(root_dir, filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontends", "js"))
    return send_from_directory(root_dir, filename)

@app.route("/img/<path:filename>")
def serve_img(filename):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontends", "img"))
    return send_from_directory(root_dir, filename)

@app.route("/<path:filename>")
def serve_root_static(filename):
    if os.path.exists(os.path.join(BOT_ROOT, filename)):
        return send_from_directory(BOT_ROOT, filename)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontends"))
    return send_from_directory(root_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)