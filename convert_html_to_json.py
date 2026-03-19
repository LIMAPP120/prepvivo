import re
import json5
import json
import os
from glob import glob

def extract_vocabulary_from_html(filepath):
    """Extract the originalVocabulary array from an HTML file and convert to our JSON format using json5."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for 'const originalVocabulary = [' ... '];'
    pattern = r'const originalVocabulary\s*=\s*(\[.*?\]);'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"No vocabulary array found in {filepath}")
        return None

    array_str = match.group(1)

    try:
        # Use json5 to parse the JavaScript array
        data = json5.loads(array_str)
    except Exception as e:
        print(f"json5 decode error in {filepath}: {e}")
        return None

    # Build our exam structure
    basename = os.path.basename(filepath).replace('.html', '')
    m = re.match(r'V(\d+)\s+(\d+)-(\d+)', basename)
    if m:
        list_num = m.group(1)
        start = m.group(2)
        end = m.group(3)
        title = f"Vocabulary List {list_num} (Words {start}-{end})"
        description = f"Test your knowledge of words {start} to {end}"
    else:
        title = basename.replace('_', ' ').replace('-', ' ')
        description = "Vocabulary practice"

    exam_json = {
        "title": title,
        "description": description,
        "time_limit": 20,
        "questions": []
    }

    for idx, item in enumerate(data, start=1):
        explanation = item.get('definition', '')
        if item.get('partOfSpeech'):
            explanation = f"({item['partOfSpeech']}) {explanation}"

        options = []
        correct_option_text = item.get('correctOption')
        opts = item.get('options', [])
        for opt_idx, opt_text in enumerate(opts, start=1):
            options.append({
                "text": opt_text,
                "is_correct": (opt_text == correct_option_text),
                "order": opt_idx
            })

        question = {
            "text": item.get('word', ''),
            "order": idx,
            "points": 1,
            "explanation": explanation,
            "options": options
        }
        exam_json["questions"].append(question)

    return exam_json

def main():
    html_files = glob("V*.html")
    if not html_files:
        print("No V*.html files found.")
        return

    for html_file in html_files:
        print(f"Processing {html_file}...")
        exam_data = extract_vocabulary_from_html(html_file)
        if exam_data:
            json_file = html_file.replace('.html', '.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(exam_data, f, indent=2, ensure_ascii=False)
            print(f"  -> Saved {json_file}")
        else:
            print(f"  -> Skipped {html_file}")

if __name__ == "__main__":
    main()