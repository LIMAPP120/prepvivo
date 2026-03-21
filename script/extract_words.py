import json
import re
import csv
import os
from collections import defaultdict

# Regex to match filename pattern like "123-456.json"
pattern = re.compile(r'^(\d+)-(\d+)\.json$')

# Collect all matching JSON files
files = []
for fname in os.listdir('.'):
    if not fname.endswith('.json'):
        continue
    match = pattern.match(fname)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        files.append((start, end, fname))

# Sort by start number to ensure correct order
files.sort(key=lambda x: x[0])

# Total expected words: last end should be 1840
total_words = 1840
words_original = []  # will hold words in order
current_num = 1

for start, end, fname in files:
    # Optional: verify that the range is contiguous (start should be current_num)
    if start != current_num:
        print(f"Warning: expected start {current_num} but file {fname} starts at {start}")
    with open(fname, 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = data.get('questions', [])
    for q in questions:
        word = q.get('text', '')
        if word:
            words_original.append(word)
            current_num += 1
        else:
            print(f"Warning: missing 'text' in {fname} at order {q.get('order')}")

# Verify we got 1840 words
if len(words_original) != total_words:
    print(f"Warning: expected {total_words} words, got {len(words_original)}")
else:
    print(f"Successfully collected {len(words_original)} words.")

# Write first CSV (original case)
with open('vocabulary_words.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['number', 'word'])
    for i, word in enumerate(words_original, start=1):
        writer.writerow([i, word])

# Write second CSV (lowercase)
with open('vocabulary_words_lowercase.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['number', 'word'])
    for i, word in enumerate(words_original, start=1):
        writer.writerow([i, word.lower()])

# Find and report duplicate words
word_positions = defaultdict(list)
for idx, word in enumerate(words_original, start=1):
    word_positions[word].append(idx)

duplicates = {word: positions for word, positions in word_positions.items() if len(positions) > 1}
if duplicates:
    print("\nDuplicate words found:")
    for word, positions in duplicates.items():
        print(f"  '{word}' appears at positions: {positions}")
else:
    print("\nNo duplicate words found.")