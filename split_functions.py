import os
from utils import find_functions

SOURCE_FILE = input("Input file (default): ") or "Rome.c"
OUTPUT_DIR = os.path.splitext(SOURCE_FILE)[0].lower() + "_functions"
STATE = {"text": None, "functions": [], "reported_dirs": set()}

def load_source():
    with open(SOURCE_FILE, "r") as f:
        STATE["text"] = f.read()

def group_suffix(name):
    if name.startswith("FUN_") and len(name) >= 7:
        return name[4:7]
    return name[:3] if len(name) >= 3 else name

def write_functions():
    text = STATE["text"]
    for start, end, name in STATE["functions"]:
        suffix = group_suffix(name)
        sub_dir = os.path.join(OUTPUT_DIR, suffix)
        if sub_dir not in STATE["reported_dirs"]:
            print(f"Writing {sub_dir}")
            STATE["reported_dirs"].add(sub_dir)
        os.makedirs(sub_dir, exist_ok=True)
        out_path = os.path.join(sub_dir, name + ".c")
        with open(out_path, "w") as f:
            f.write(text[start:end + 1])

if __name__ == "__main__":
    print("Loading source")
    load_source()
    print("Finding functions")
    STATE["functions"] = find_functions(STATE["text"])
    print("Writing functions")
    write_functions()
    print(f"Wrote {len(STATE['functions'])} functions")
