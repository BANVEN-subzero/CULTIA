
import os
import sys
from dotenv import load_dotenv

# Add parent directory to import api
sys.path.insert(0, os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cultureAI")))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "cultureAI", ".env"))

# Import the function from api.py
from api import call_gemini_fallback

print("--- CULTIA Gemini Fallback Test ---")
print()

# Test questions (not in local database for sure!)
test_questions = [
    "Tell me about the Mankon people of Cameroon",
    "What are the traditions of the Ngemba people?",
    "What is the history of the Kom people?",
    "Tell me about Tikar bronze casting techniques",
    "What are some traditional Fulani herding practices in Cameroon?"
]

for i, question in enumerate(test_questions, 1):
    print(f"Test Question {i}: {question}")
    print("-" * 60)
    
    response = call_gemini_fallback(question)
    
    if response:
        print("✅ Gemini Response Received:")
        print(response[:500] + ("..." if len(response) > 500 else ""))
    else:
        print("❌ Gemini Fallback Failed!")
    
    print()
    print("=" * 60)
    print()

print("--- Test Complete ---")
