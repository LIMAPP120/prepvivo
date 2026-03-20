import os
import re
import sys

def rename_json_files(directory='.'):
    """
    Renames JSON files of the form 'X-Y.json' to '(X-10)-(Y-10).json'
    for all files where X >= 671.
    """
    pattern = re.compile(r'^(\d+)-(\d+)\.json$')
    
    for filename in os.listdir(directory):
        if not filename.endswith('.json'):
            continue
        
        match = pattern.match(filename)
        if not match:
            print(f"Skipping (does not match pattern): {filename}")
            continue
        
        start = int(match.group(1))
        end = int(match.group(2))
        
        if start < 671:
            print(f"Skipping (start < 671): {filename}")
            continue
        
        new_start = start - 10
        new_end = end - 10
        new_filename = f"{new_start}-{new_end}.json"
        
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        
        if os.path.exists(new_path):
            print(f"Warning: {new_filename} already exists. Skipping {filename}.")
            continue
        
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}")

if __name__ == '__main__':
    # You can pass a target directory as a command-line argument
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    rename_json_files(target_dir)
    