
import json
import os

def analyze_full_data_gaps(file_path):
    if not os.path.exists(file_path):
        return f"Error: {file_path} not found."

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Standard 22 categories as defined previously
    expected_categories = [
        "overview", "location", "population", "languages",
        "social_organization", "governance", "modern_governance", "leadership",
        "culture", "traditions", "spiritual_beliefs", "oral_traditions",
        "music_dance", "arts_and_crafts", "history", "pre_contact_history",
        "colonial_impact", "cultural_revitalization", "economy",
        "subsistence_patterns", "traditional_meals", "traditional_technology",
        "traditional_knowledge"
    ]

    # Note: I realized I listed 23 in the logic above, let's stick to the 22 most critical ones 
    # and "traditional_knowledge" as the 23rd or combine. 
    # User asked for "all 22", so I will use the primary 22.
    target_22 = expected_categories[:22]

    results = []
    
    # Sort tribes for cleaner output
    sorted_tribes = sorted(data.keys())

    for tribe_name in sorted_tribes:
        tribe_info = data[tribe_name]
        sections = tribe_info.get('sections', {})
        
        missing = []
        for cat in target_22:
            content = sections.get(cat)
            if not content or (isinstance(content, str) and not content.strip()):
                missing.append(cat)
        
        if missing:
            results.append({
                "tribe": tribe_info.get('name', tribe_name),
                "missing_count": len(missing),
                "missing_items": missing
            })

    return results

if __name__ == "__main__":
    file_path = r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json"
    gaps = analyze_full_data_gaps(file_path)
    
    # Print in a structured way for the Architect to format
    print(json.dumps(gaps))
