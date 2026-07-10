import os
import sys

STATE = {
    "file_name": "Rome.c",
    "output_dir": "string_evaluation_candidates",
    "lines": [],
    "functions": [],
    "candidates": []
}

def load_file():
    print("Loading files")
    if len(sys.argv) > 1:
        STATE["file_name"] = sys.argv[1]
    with open(STATE["file_name"], "r", encoding="utf-8", errors="ignore") as f:
        STATE["lines"] = f.readlines()

def parse_functions():
    print("Parsing functions")
    func_prefixes = ("void FUN_", "int FUN_", "long FUN_", "undefined", "ulong FUN_", "char FUN_", "double FUN_", "float FUN_", "short FUN_")
    start_idx = -1
    for i, line in enumerate(STATE["lines"]):
        if line.startswith(func_prefixes):
            if start_idx != -1:
                STATE["functions"].append((start_idx, i))
            start_idx = i
    if start_idx != -1:
        STATE["functions"].append((start_idx, len(STATE["lines"])))

def analyze_functions():
    print("Analyzing functions")
    for start, end in STATE["functions"]:
        body_lines = STATE["lines"][start:end]
        has_loop = False
        has_subtraction = False
        has_stride = False
        has_array_access = False
        for line in body_lines:
            if "while (" in line or "for (" in line or "do {" in line:
                has_loop = True
            if "-=" in line or " - " in line or "--" in line:
                has_subtraction = True
            if "+=" in line or " + " in line or "++" in line:
                has_stride = True
            if "[" in line and "]" in line:
                has_array_access = True
        if has_loop and has_subtraction and has_stride and has_array_access:
            check_detailed_heuristics(start, end, body_lines)

def check_detailed_heuristics(start, end, body_lines):
    stride_indicators = ("0x10", "0x14", "0x18", "0x1c", "0x20", "16", "20", "24", "28", "32")
    valid_stride = False
    for line in body_lines:
        for ind in stride_indicators:
            if ind in line and ("+" in line or "*" in line):
                valid_stride = True
                break
        if valid_stride:
            break
    if valid_stride:
        STATE["candidates"].append((start, end))

def save_candidates():
    print("Saving candidates")
    if not os.path.exists(STATE["output_dir"]):
        os.makedirs(STATE["output_dir"])
    for idx, (start, end) in enumerate(STATE["candidates"], start=1):
        out_path = os.path.join(STATE["output_dir"], f"candidate_{idx}.c")
        with open(out_path, "w", encoding="utf-8") as f:
            f.writelines(STATE["lines"][start:end])

if __name__ == "__main__":
    load_file()
    parse_functions()
    analyze_functions()
    save_candidates()
    print("Done")
