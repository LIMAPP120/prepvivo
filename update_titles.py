import json
import re

# List of files to process
files = [
    "21-40.json",
    "41-60.json",
    "61-80.json",
    "1801-1820.json",
    "1821-1837.json"
]

for filename in files:
    # Extract start and end numbers from filename using regex
    match = re.match(r'(\d+)-(\d+)\.json', filename)
    if not match:
        print(f"Skipping {filename}: does not match pattern")
        continue
    start, end = match.groups()
    
    # Read the JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update the title
    data['title'] = f"Vocabulary List (Words {start}-{end})"
    
    # Write back the JSON (with same formatting, using indent=2 to preserve readability)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {filename} -> title: {data['title']}")