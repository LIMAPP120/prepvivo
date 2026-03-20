import os
import re
from glob import glob

def rename_files():
    # Process V1 files: just remove the "V1 " prefix
    v1_files = glob("V1 *.json")
    for f in v1_files:
        # Extract the part after "V1 "
        new_name = f[3:]  # remove first 3 characters ("V1 ")
        if os.path.exists(new_name):
            print(f"Warning: {new_name} already exists, skipping {f}")
        else:
            os.rename(f, new_name)
            print(f"Renamed {f} -> {new_name}")

    # Process V2 files: offset +320
    v2_files = glob("V2 *.json")
    v2_files.sort()  # ensure order
    for f in v2_files:
        # Extract numbers using regex
        match = re.search(r'V2 (\d+)-(\d+)\.json', f)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            new_start = start + 320
            new_end = end + 320
            new_name = f"{new_start}-{new_end}.json"
            if os.path.exists(new_name):
                print(f"Warning: {new_name} already exists, skipping {f}")
            else:
                os.rename(f, new_name)
                print(f"Renamed {f} -> {new_name}")
        else:
            print(f"Could not parse {f}, skipping")

    # Process V3 files: offset +650
    v3_files = glob("V3 *.json")
    v3_files.sort()
    for f in v3_files:
        match = re.search(r'V3 (\d+)-(\d+)\.json', f)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            new_start = start + 650
            new_end = end + 650
            new_name = f"{new_start}-{new_end}.json"
            if os.path.exists(new_name):
                print(f"Warning: {new_name} already exists, skipping {f}")
            else:
                os.rename(f, new_name)
                print(f"Renamed {f} -> {new_name}")
        else:
            print(f"Could not parse {f}, skipping")

if __name__ == "__main__":
    rename_files()