import os
import shutil
from utils import group_suffix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_DIR = os.path.join(SCRIPT_DIR, "rome_functions")
LIST_FILE = os.path.join(SCRIPT_DIR, "list.txt")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "listed_functions")
MERGED_FILE = os.path.join(OUTPUT_DIR, "merged.txt")

def main():
    with open(LIST_FILE, "r") as f:
        names = set(line.strip() for line in f if line.strip())
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    missing = []
    copied = 0
    with open(MERGED_FILE, "w") as merged:
        for name in sorted(names):
            subfolder = group_suffix(name)
            src_path = os.path.join(FUNCTIONS_DIR, subfolder, name + ".c")
            if not os.path.isfile(src_path):
                missing.append(name)
                continue
            shutil.copy2(src_path, os.path.join(OUTPUT_DIR, name + ".txt"))
            with open(src_path, "r") as src:
                content = src.read()
            merged.write(content)
            if not content.endswith("\n"):
                merged.write("\n")
            merged.write("\n\n\n")
            copied += 1
    if missing:
        print(f"Functions not found in {FUNCTIONS_DIR}:")
        for name in sorted(missing):
            print(name)
    print(f"Copied {copied} functions to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
