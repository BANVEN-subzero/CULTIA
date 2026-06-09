
print("Start of script!")

import os
print("Imported os")

import google.generativeai as genai
print("Imported genai")

from google.ai.generativelanguage_v1 import GenerativeServiceClient
print("Imported GenerativeServiceClient")

from google.api_core.client_options import ClientOptions
print("Imported ClientOptions")

from dotenv import load_dotenv
print("Imported load_dotenv")

print("=== Direct v1 API Test ===")

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env")
print(f"Loading from: {env_path}")
load_dotenv(env_path)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: No API key found!")
    exit(1)

print(f"API key present: {bool(GEMINI_API_KEY)}")

try:
    print("About to create client...")
    # Explicitly set client options to use v1!
    client_options = ClientOptions(
        api_endpoint="generativelanguage.googleapis.com",
        api_key=GEMINI_API_KEY
    )

    print("\nCreating v1 GenerativeServiceClient...")
    client = GenerativeServiceClient(client_options=client_options)

    print("\nClient created successfully!")
    
    # Let's try to list models using this client
    print("\n--- Available Models ---")
    try:
        models = client.list_models()
        for model in models:
            print(f" - {model.name}: {model.display_name}")
    except Exception as e:
        print(f"ERROR listing models: {type(e)} {e}")
        import traceback
        print(traceback.format_exc())

    print("\n--- Now trying to generate content ---")
    test_prompt = "Tell me about the Mankon people of Cameroon in 2-3 sentences."

    # Use the correct model name for v1: "gemini-1.5-flash"!
    model_name = "models/gemini-1.5-flash"
    print(f"Using model: {model_name}")

    try:
        # Build the request
        response = client.generate_content(
            model=model_name,
            contents=[{"parts": [{"text": test_prompt}]}]
        )
        print("SUCCESS! Response received!")
        print(f"\n{response}")
        print("\n--- Extracted Text ---")
        if hasattr(response, "candidates") and len(response.candidates) > 0:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            print(part.text)
    except Exception as e:
        print(f"\nERROR generating content: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== Test Complete ===")
