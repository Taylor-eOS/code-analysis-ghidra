from utils import find_function_boundaries
import os

SOURCE_FILE = "Rome.c"
OUTPUT_DIR = "functions"
STATE = {"lines": None, "starts": [], "ends": []}

def load_source():
    with open(SOURCE_FILE, "r") as f:
        STATE["lines"] = f.readlines()

def find_ends():
    lines = STATE["lines"]
    ends = []
    for start in STATE["starts"]:
        end = start
        for i in range(start, len(lines)):
            if lines[i].rstrip() == "}":
                end = i
                break
        ends.append(end)
    STATE["ends"] = ends

def write_functions():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lines = STATE["lines"]
    starts = STATE["starts"]
    ends = STATE["ends"]
    for start, end in zip(starts, ends):
        line = lines[start]
        idx = line.find("FUN_")
        name_end = line.find("(", idx)
        name = line[idx:name_end].strip()
        out_path = os.path.join(OUTPUT_DIR, name + ".c")
        with open(out_path, "w") as f:
            f.writelines(lines[start:end + 1])

def main():
    load_source()
    STATE["starts"] = find_function_boundaries(STATE["lines"])
    find_ends()
    write_functions()
    print(f"Wrote {len(STATE['starts'])} functions to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
