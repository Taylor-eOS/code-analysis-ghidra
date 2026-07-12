from utils import find_functions

SOURCE_FILE = "Rome.c"
LIST_FILE = "list.txt"
OUTPUT_FILE = "extracted_functions.txt"
STATE = {"names": None, "text": None, "spans": None}

def load_names():
    print("Loading names")
    with open(LIST_FILE, "r") as f:
        STATE["names"] = set(line.strip() for line in f if line.strip())

def load_source():
    print("Loading source")
    with open(SOURCE_FILE, "r") as f:
        STATE["text"] = f.read()

def index_spans():
    spans = {}
    for decl_start, close, name in find_functions(STATE["text"]):
        if name in STATE["names"] and name not in spans:
            spans[name] = (decl_start, close)
    STATE["spans"] = spans

def write_output():
    spans = STATE["spans"]
    text = STATE["text"]
    missing = STATE["names"] - set(spans.keys())
    written = 0
    with open(OUTPUT_FILE, "w") as f:
        for name in STATE["names"]:
            if name not in spans:
                continue
            decl_start, close = spans[name]
            f.write(text[decl_start:close + 1])
            f.write("\n\n")
            written += 1
    if missing:
        print(f"Missing functions not found in {SOURCE_FILE}:")
        for name in sorted(missing):
            print(name)
        print(f"List basenames with no folder or ending.")
    print(f"Wrote {written} functions to {OUTPUT_FILE}")

def main():
    load_names()
    load_source()
    index_spans()
    write_output()

if __name__ == "__main__":
    main()
