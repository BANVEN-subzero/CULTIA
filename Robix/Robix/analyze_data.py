
import json
import os

def analyze_tribes_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # If the JSON is wrapped in a 'tribes' key
    tribes = data.get('tribes', data)
    
    # Standard categories we expect
    expected_categories = [
        "overview", "history", "culture", "traditions", 
        "arts_and_crafts", "economy", "governance", 
        "location", "population", "languages", 
        "spiritual_beliefs", "social_organization", 
        "traditional_technology", "music_dance", 
        "pre_contact_history", "colonial_impact", 
        "modern_governance", "cultural_revitalization", 
        "oral_traditions", "traditional_knowledge", 
        "subsistence_patterns", "traditional_meals"
    ]

    report = {
        "completely_empty": [],
        "partially_empty": {}
    }

    for tribe_name, tribe_info in tribes.items():
        sections = tribe_info.get('sections', {})
        if not sections:
            report["completely_empty"].append(tribe_name)
            continue
        
        missing = []
        for cat in expected_categories:
            content = sections.get(cat)
            if not content or (isinstance(content, str) and not content.strip()):
                missing.append(cat)
        
        if missing:
            report["partially_empty"][tribe_name] = missing

    return report

if __name__ == "__main__":
    file_path = r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json"
    results = analyze_tribes_data(file_path)
    
    print("\n--- TRIBES WITH NO INFORMATION AT ALL ---")
    if not results["completely_empty"]:
        print("None (All tribes have at least some data)")
    else:
        for tribe in results["completely_empty"]:
            print(f"- {tribe}")

    print("\n--- TRIBES WITH MISSING CATEGORIES ---")
    missing_counts = {}
    for tribe, missing in results["partially_empty"].items():
        print(f"- {tribe}: Missing {len(missing)} categories")
        for m in missing:
            missing_counts[m] = missing_counts.get(m, 0) + 1
    
    print("\n--- FREQUENCY OF MISSING CATEGORIES ---")
    sorted_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_missing:
        print(f"- {cat}: {count} tribes missing this")
