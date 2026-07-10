from bisect import bisect_right
from utils import find_functions

SOURCE_FILE = "Rome.c"
LINE_LIST_FILE = "line_list.txt"
OUTPUT_FILE = "extracted_functions.txt"
STATE = {"text": None, "line_starts": None, "spans": None, "target_lines": None}

def load_source():
    with open(SOURCE_FILE, "r") as f:
        STATE["text"] = f.read()

def load_target_lines():
    with open(LINE_LIST_FILE, "r") as f:
        STATE["target_lines"] = set(int(l.strip()) for l in f if l.strip())

def index_line_starts():
    text = STATE["text"]
    starts = [0]
    for i, c in enumerate(text):
        if c == "\n":
            starts.append(i + 1)
    STATE["line_starts"] = starts

def offset_to_line(offset):
    return bisect_right(STATE["line_starts"], offset)

def index_spans():
    STATE["spans"] = [(decl_start, close) for decl_start, close, name in find_functions(STATE["text"])]

def find_containing_span(line_no):
    line_starts = STATE["line_starts"]
    offset = line_starts[line_no - 1]
    for start, end in STATE["spans"]:
        if start <= offset <= end:
            return start, end
    return None

def write_output():
    text = STATE["text"]
    written_spans = set()
    missing = []
    written = 0
    with open(OUTPUT_FILE, "w") as f:
        for line_no in sorted(STATE["target_lines"]):
            span = find_containing_span(line_no)
            if span is None:
                missing.append(line_no)
                continue
            if span in written_spans:
                continue
            written_spans.add(span)
            start, end = span
            f.write(text[start:end + 1])
            f.write("\n\n")
            written += 1
    if missing:
        print("Lines not contained in any known function:")
        for ln in missing:
            print(ln)
    print(f"Wrote {written} functions to {OUTPUT_FILE}")

def main():
    load_source()
    load_target_lines()
    index_line_starts()
    index_spans()
    write_output()

if __name__ == "__main__":
    main()
