import os
import shutil
from split_functions import group_suffix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_DIR = os.path.join(SCRIPT_DIR, "rome_functions")
LIST_FILE = os.path.join(SCRIPT_DIR, "list.txt")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "extracted_functions")

def main():
    with open(LIST_FILE, "r") as f:
        names = set(line.strip() for line in f if line.strip())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    missing = []
    copied = 0
    for name in names:
        subfolder = group_suffix(name)
        src_path = os.path.join(FUNCTIONS_DIR, subfolder, name + ".c")
        if not os.path.isfile(src_path):
            missing.append(name)
            continue
        shutil.copy2(src_path, os.path.join(OUTPUT_DIR, name + ".c"))
        copied += 1
    if missing:
        print(f"Functions not found in {FUNCTIONS_DIR}:")
        for name in sorted(missing):
            print(name)
    print(f"Copied {copied} functions to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
