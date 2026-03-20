import json
import re
import os

# Get all .json files in the current directory
for filename in os.listdir('.'):
    if not filename.endswith('.json'):
        continue

    # Extract start and end numbers from filename using regex
    match = re.match(r'^(\d+)-(\d+)\.json$', filename)
    if not match:
        # Skip files that don't match the pattern (like other .json files)
        print(f"Skipping (does not match pattern): {filename}")
        continue

    start, end = match.groups()

    # Read the JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update the title (overwrite whatever was there)
    data['title'] = f"Vocabulary List (Words {start}-{end})"

    # Write back the JSON with the same indentation (2 spaces for readability)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {filename} -> title: {data['title']}")