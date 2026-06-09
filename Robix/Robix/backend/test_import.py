
import sys
import os

print("=== Starting import test ===")
print(f"Current working dir: {os.getcwd()}")

# Add .. to path
cultureAI_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cultureAI'))
print(f"cultureAI dir: {cultureAI_dir}")
sys.path.insert(0, cultureAI_dir)
print(f"sys.path now is: {sys.path}")

print("\nTrying to import cameroon_chatbot...")
try:
    from cameroon_chatbot import AdvancedTribesBot
    print("✅ Successfully imported AdvancedTribesBot!")
except Exception as e:
    print(f"❌ Error importing cameroon_chatbot: {type(e).__name__}: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== Done ===")
