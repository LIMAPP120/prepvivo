import json
import re
import os

# Define the allowed numeric range
MIN_START = 1
MAX_END = 1840

# Get all .json files in the current directory
for filename in os.listdir('.'):
    if not filename.endswith('.json'):
        continue

    # Extract start and end numbers from filename using regex
    match = re.match(r'^(\d+)-(\d+)\.json$', filename)
    if not match:
        print(f"Skipping (does not match pattern): {filename}")
        continue

    start = int(match.group(1))
    end = int(match.group(2))

    # Only process files within the desired range
    if not (MIN_START <= start <= MAX_END and end <= MAX_END):
        print(f"Skipping (outside range {MIN_START}-{MAX_END}): {filename}")
        continue

    # Read the JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update the description field
    if 'description' in data:
        old_desc = data['description']
        data['description'] = "Test your knowledge of words"
        print(f"Updated {filename}: description changed from '{old_desc}' to '{data['description']}'")
    else:
        print(f"Warning: {filename} has no 'description' field. Adding it.")
        data['description'] = "Test your knowledge of words"

    # Write back the JSON with the same indentation (2 spaces)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)