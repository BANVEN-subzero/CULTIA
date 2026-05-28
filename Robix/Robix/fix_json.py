
import json
import os

def fix_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to find where it breaks
    try:
        json.loads(content)
        print("JSON is already valid.")
        return
    except json.JSONDecodeError as e:
        print(f"Error at {e.pos}: {e}")
        # Let's see if there's a missing comma or extra brace
        # Char 52143 is where line 763 starts (approximately)
        
        # We know char 52143 is the issue.
        # Looking at previous context:
        #   },
        #   "bassa": {
        
        # If line 763 closes the root, it means there's a root-level closing brace too early.
        # I'll try to find all root-level closing braces.
        
        stack = 0
        fixed_content = ""
        for i, char in enumerate(content):
            if char == '{':
                stack += 1
            elif char == '}':
                stack -= 1
            
            # If stack goes to 0 but it's not the end of the file, we might have a problem.
            if stack == 0 and i < len(content) - 5 and char == '}':
                # Check if next non-whitespace char is a comma or "
                remaining = content[i+1:].strip()
                if remaining.startswith(',') or remaining.startswith('"'):
                    print(f"Found premature closing brace at position {i}. Removing it.")
                    # Skip this character
                    continue
            
            fixed_content += char
            
        # Try to load the fixed content
        try:
            json.loads(fixed_content)
            print("Successfully fixed JSON!")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
        except json.JSONDecodeError as e2:
            print(f"Still failing at {e2.pos}: {e2}")
            # Try a more aggressive approach: find all tribes and re-assemble
            pass

if __name__ == "__main__":
    fix_json_file(r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json")
