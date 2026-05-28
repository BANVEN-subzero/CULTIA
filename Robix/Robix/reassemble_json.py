
import json
import re

def reassemble_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all top-level keys and their values
    # This is tricky because values are nested objects.
    # I'll try to find all '"tribe_name": {' patterns at the top level (indent 2)
    
    tribes = {}
    pattern = re.compile(r'^\s{2}"([a-z_]+)":\s*\{', re.MULTILINE)
    matches = list(pattern.finditer(content))
    
    for i, match in enumerate(matches):
        tribe_name = match.group(1)
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else content.rfind('}')
        
        tribe_content_str = content[start:end].strip()
        # Remove trailing comma if it exists
        if tribe_content_str.endswith(','):
            tribe_content_str = tribe_content_str[:-1]
        
        # Wrap in braces to make it a valid object for parsing
        try:
            tribe_obj = json.loads("{" + tribe_content_str + "}")
            tribes.update(tribe_obj)
        except json.JSONDecodeError:
            # If parsing fails, try to clean it up (remove extra braces)
            cleaned = tribe_content_str
            # Count braces
            balance = 0
            valid_end = 0
            for j, c in enumerate(cleaned):
                if c == '{': balance += 1
                elif c == '}': balance -= 1
                if balance == 0 and j > 0:
                    valid_end = j + 1
                    break
            
            if valid_end > 0:
                try:
                    tribe_obj = json.loads("{" + cleaned[:valid_end] + "}")
                    tribes.update(tribe_obj)
                except:
                    print(f"Failed to parse tribe: {tribe_name}")
            else:
                print(f"Failed to find end of tribe: {tribe_name}")

    # Write back clean JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tribes, f, indent=2)
    print(f"Reassembled {len(tribes)} tribes.")

if __name__ == "__main__":
    reassemble_json(r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json")
