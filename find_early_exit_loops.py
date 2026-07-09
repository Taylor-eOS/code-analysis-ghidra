import os
import re

STATE = {
    "file_name": "Rome.c",
    "output_dir": "early_exit_loops",
    "file_lines": [],
    "func_bounds": [],
    "hits": []
}

FUNC_START_PREFIXES = ("void FUN_", "int FUN_", "long FUN_", "undefined", "ulong FUN_", "char FUN_", "double FUN_", "float FUN_")
LOOP_RE = re.compile(r"\b(do\s*\{|while\s*\(|for\s*\()")
ACCUM_RE = re.compile(r"(\w+)\s*=\s*\1\s*[+\-]")
BREAK_RETURN_RE = re.compile(r"\b(break|return)\b")
IF_BREAK_RETURN_RE = re.compile(r"if\s*\(([^)]*)\)\s*\{?\s*$")
FLOAT_LITERAL_RE = re.compile(r"\b0\.\d+\b|\bDAT_0[0-9a-fA-F]+\b.*(?:float|\(float\))|\(float\)")
FRACTIONAL_HEX_FLOAT_RE = re.compile(r"0x3[0-9a-fA-F]{7}\b")

def load_file():
    with open(STATE["file_name"], "r", encoding="utf-8", errors="ignore") as f:
        STATE["file_lines"] = f.readlines()

def find_function_bounds():
    lines = STATE["file_lines"]
    starts = []
    for i, line in enumerate(lines):
        if line.startswith(FUNC_START_PREFIXES):
            starts.append(i)
    starts.append(len(lines))
    STATE["func_bounds"] = [(starts[i], starts[i + 1]) for i in range(len(starts) - 1)]

def has_float_threshold(full_text):
    if FLOAT_LITERAL_RE.search(full_text):
        return True
    if FRACTIONAL_HEX_FLOAT_RE.search(full_text):
        return True
    return False

def find_candidates():
    hits = []
    for start, end in STATE["func_bounds"]:
        lines = STATE["file_lines"][start:end]
        full = "".join(lines)
        if not LOOP_RE.search(full):
            continue
        accum_vars = set(m.group(1) for m in ACCUM_RE.finditer(full))
        if not accum_vars:
            continue
        loop_start_idx = None
        for i, line in enumerate(lines):
            if LOOP_RE.search(line):
                loop_start_idx = i
                break
        if loop_start_idx is None:
            continue
        body = lines[loop_start_idx:]
        found = False
        for i, line in enumerate(body):
            if not BREAK_RETURN_RE.search(line):
                continue
            j = i - 1
            checked = 0
            while j >= 0 and checked < 3:
                m = IF_BREAK_RETURN_RE.search(body[j])
                if m:
                    cond = m.group(1)
                    if any(re.search(r"\b" + re.escape(v) + r"\b", cond) for v in accum_vars):
                        found = True
                    break
                if body[j].strip() != "":
                    checked += 1
                j -= 1
            if found:
                break
        if found:
            if has_float_threshold(full):
                hits.append((start, end))
    STATE["hits"] = hits

def save_hits():
    if not os.path.exists(STATE["output_dir"]):
        os.makedirs(STATE["output_dir"])
    for idx, (start, end) in enumerate(STATE["hits"], start=1):
        file_path = os.path.join(STATE["output_dir"], f"hit_{idx}.c")
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(STATE["file_lines"][start:end])

if __name__ == "__main__":
    if not os.path.exists(STATE["file_name"]):
        print(f"File not found: {STATE['file_name']}")
    else:
        load_file()
        find_function_bounds()
        find_candidates()
        save_hits()
        print(f"Candidates: {len(STATE['hits'])}")
        print("Done")
