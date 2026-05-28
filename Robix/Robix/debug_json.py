
import json

def find_json_error(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        json.loads(content)
        print("JSON is valid.")
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        print(f"Context: {content[e.pos-50:e.pos+50]}")

if __name__ == "__main__":
    find_json_error(r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json")
