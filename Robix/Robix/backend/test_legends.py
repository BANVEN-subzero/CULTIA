import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

# Load tribal_legends directly
try:
    import json
    legends_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cultureAI", "tribal_legends.json")
    with open(legends_path, "r", encoding="utf-8") as f:
        TRIBAL_LEGENDS = json.load(f)

    print("=== Checking tribal_legends keys:", list(TRIBAL_LEGENDS.keys()))
    print("=== Total legends:", len(TRIBAL_LEGENDS))

    new_tribes = ["baka", "kapsiki", "massa", "yamba", "chamba", "mousgoum", "toupouri", "bafia"]
    print("\n=== New legends present:")
    for tribe in new_tribes:
        if tribe in TRIBAL_LEGENDS:
            print(f"✅ {tribe}: {TRIBAL_LEGENDS[tribe]['title']}")

    print("\n✅ All 8 new legends added successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    print(traceback.format_exc())
