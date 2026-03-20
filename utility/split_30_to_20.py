import json
import glob
import os
import re

def process_files():
    # Find all JSON files (excluding our output file)
    json_files = glob.glob("*.json")
    output_file = "extracted_questions.json"
    if output_file in json_files:
        json_files.remove(output_file)

    all_extracted = []

    for filename in sorted(json_files):
        # Only process files that match the pattern like 321-350.json (numbers)
        if not re.match(r'\d+-\d+\.json', filename):
            continue

        print(f"Processing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = data.get("questions", [])
        if len(questions) < 30:
            print(f"  Skipping {filename}: has only {len(questions)} questions.")
            continue

        # Keep first 20 in the original file
        first_20 = questions[:20]
        last_10 = questions[20:30]   # indices 20 to 29 (10 questions)

        # Update original file
        data["questions"] = first_20
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Collect last 10 (without order numbers)
        for q in last_10:
            # Remove the existing order so we can reassign later
            q.pop("order", None)
            all_extracted.append(q)

        print(f"  -> Kept first 20, extracted last 10 from {filename}")

    # Now create a new exam with all extracted questions
    if all_extracted:
        # Reassign order numbers sequentially
        for idx, q in enumerate(all_extracted, start=1):
            q["order"] = idx

        extracted_exam = {
            "title": "Extracted Vocabulary Questions (Last 10 from each list)",
            "description": "Combined last 10 questions from all vocabulary lists (words 321‑650).",
            "time_limit": 20,   # same as original
            "questions": all_extracted
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_exam, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Created '{output_file}' with {len(all_extracted)} extracted questions.")
    else:
        print("No questions extracted.")

if __name__ == "__main__":
    process_files()