
import os
from dotenv import load_dotenv

print("=== Standalone Gemini Test ===")

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env")
print(f"Loading environment from: {env_path}")
load_dotenv(env_path)

try:
    import google.generativeai as genai
    print("[OK] google-generativeai imported successfully!")
except ImportError as e:
    print(f"[ERROR] Failed to import google-generativeai: {e}")
    exit(1)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
print(f"API Key present: {bool(GEMINI_API_KEY)}")

if not GEMINI_API_KEY:
    print("[ERROR] API key not found!")
    exit(1)

try:
    # Configure to use the v1 API explicitly!
    from google.api_core.client_options import ClientOptions
    client_options = ClientOptions(api_endpoint="generativelanguage.googleapis.com")
    
    genai.configure(api_key=GEMINI_API_KEY, client_options=client_options)
    print("[OK] API configured successfully!")
except Exception as e:
    print(f"[ERROR] API configuration failed: {e}")
    import traceback
    print(traceback.format_exc())
    exit(1)

# Test a question
test_question = "Tell me about the Mankon people of Cameroon"

print(f"\nTesting question: {test_question}")

# Try various model name formats!
models_to_test = [
    'gemini-1.5-flash', 
    'gemini-1.5-pro', 
    'gemini-pro', 
    'gemini-2.0-flash-exp'
]
model_name = None  # Will be set later

response_found = False

for model_candidate in models_to_test:
    model_name = model_candidate
    try:
        print(f"\nTrying model: {model_name}")
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 2048
            }
        )
        
        prompt = (
            "You are CULTIA, a warm, knowledgeable, and passionate cultural companion "
            "who specializes in Cameroonian tribal cultures, traditions, history, languages, "
            "and ethnic groups. Your mission is to educate, inspire, and connect people with "
            "the rich cultural heritage of Cameroon.\n"
            "CRITICAL RULES:\n"
            "1. ABSOLUTELY NO markdown formatting (no asterisks, no hashes, no bold/italic markers)\n"
            "2. Use only plain, conversational text\n"
            "3. Focus ONLY on Cameroonian cultures and tribes\n"
            "4. Be specific, detailed, and culturally authentic\n\n"
            f"User Question: {test_question}"
        )
        
        print("Calling Gemini...")
        response = model.generate_content(prompt)
        
        if response:
            if hasattr(response, 'text') and response.text:
                print("\n[OK] Success! Response received:")
                print("-" * 60)
                print(response.text)
                print("-" * 60)
                response_found = True
                break
            elif hasattr(response, 'parts') and len(response.parts) > 0:
                full_text = ''.join(p.text for p in response.parts if hasattr(p, 'text'))
                if full_text:
                    print("\n[OK] Success! Response received (parts):")
                    print("-" * 60)
                    print(full_text)
                    print("-" * 60)
                    response_found = True
                    break
            else:
                print(f"\n[WARN] Response exists but has no usable text: {response}")
        else:
            print("\n[ERROR] No response received from model!")
            
    except Exception as e:
        print(f"\n[ERROR] Error calling model {model_name}: {type(e).__name__}: {e}")
        # Don't print full traceback here, just the error

if not response_found:
    print("\n[ERROR] All models failed!")

print("\n=== Test Finished ===")
