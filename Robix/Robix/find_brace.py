
def find_unmatched_brace(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stack = []
    for i, char in enumerate(content):
        if char == '{':
            stack.append(i)
        elif char == '}':
            if not stack:
                print(f"Unmatched closing brace at char {i}")
                return
            stack.pop()
            if not stack:
                print(f"Root object closed at char {i} (line {content.count('\n', 0, i) + 1})")
                print(f"Next characters: {content[i+1:i+50]!r}")
                return

if __name__ == "__main__":
    find_unmatched_brace(r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json")
