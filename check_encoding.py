import os
import re

def find_open_without_encoding(start_dir):
    pattern = re.compile(r'open\s*\([^)]+\)')
    for root, dirs, files in os.walk(start_dir):
        if 'venv' in root or '.git' in root or 'node_modules' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for match in matches:
                            if 'encoding' not in match and '"wb"' not in match and "'wb'" not in match and '"rb"' not in match and "'rb'" not in match:
                                print(f"Found unsafe open in {path}: {match}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    find_open_without_encoding('.')
