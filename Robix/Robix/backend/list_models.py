
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env"))

try:
    from google import genai
    
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("--- Available Models ---")
        models = client.models.list()
        for model in models:
            print(f"\nName: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Description: {model.description}")
    else:
        print("API key not found!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())
