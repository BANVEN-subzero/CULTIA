
print("Start REST test!")

import requests
import os
from dotenv import load_dotenv

print("Imports done.")

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env")
load_dotenv(env_path)
print(".env loaded.")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: No API key!")
    exit(1)

print("API key found.")

# Use v1 API endpoint with gemini-2.0-flash
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Request body
data = {
    "contents": [
        {
            "parts": [
                {"text": "Tell me about the Mankon people of Cameroon in 2-3 sentences."}
            ]
        }
    ]
}

print("About to send request...")
try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()  # Raise exception for HTTP errors
    print("Request successful!")
    
    result = response.json()
    print("\nResponse JSON:")
    print(result)
    
    print("\n--- Extracted Text ---")
    if "candidates" in result and len(result["candidates"]) > 0:
        candidate = result["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            parts = candidate["content"]["parts"]
            for part in parts:
                if "text" in part:
                    print(part["text"])

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())

print("\nTest complete.")
