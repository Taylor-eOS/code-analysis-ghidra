from utils import find_functions

SOURCE_FILE = "Rome.c"
TRUNCATED_FILE = "Rome_truncated.c"
BUCKETS = 100
RENAMED_MIN_LEN = 12
STATE = {"text": None, "lines": None, "line_offsets": None, "buckets": [False] * BUCKETS, "renamed_lines": []}

def load_source():
    print("Loading source")
    with open(SOURCE_FILE, "r") as f:
        STATE["text"] = f.read()
    STATE["lines"] = STATE["text"].splitlines(keepends=True)
    offsets = []
    pos = 0
    for line in STATE["lines"]:
        offsets.append(pos)
        pos += len(line)
    STATE["line_offsets"] = offsets

def offset_to_line(offset):
    offsets = STATE["line_offsets"]
    lo = 0
    hi = len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo

def analyze_functions():
    print("Analyzing functions")
    total_lines = len(STATE["lines"])
    if total_lines == 0:
        return
    functions = find_functions(STATE["text"])
    renamed_lines = []
    for start, end, name in functions:
        if len(name) > RENAMED_MIN_LEN:
            renamed_lines.append(offset_to_line(start))
    STATE["renamed_lines"] = renamed_lines
    for i in renamed_lines:
        bucket_idx = min(int((i / total_lines) * BUCKETS), BUCKETS - 1)
        STATE["buckets"][bucket_idx] = True

def draw_visualization():
    print("Drawing visualization")
    bar = "["
    for bucket in STATE["buckets"]:
        if bucket:
            bar += "\033[91m█\033[0m"
        else:
            bar += "\033[97m█\033[0m"
    bar += "]"
    print("Codebase distribution (Red: Renamed, White: Unmodified)")
    print("0% " + bar + " 100%")
    total_lines = len(STATE["lines"])
    if total_lines == 0:
        return
    start_bucket = 0
    current_state = STATE["buckets"][0]
    for idx in range(1, BUCKETS):
        if STATE["buckets"][idx] != current_state:
            start_line = int((start_bucket / BUCKETS) * total_lines) + 1
            end_line = int((idx / BUCKETS) * total_lines)
            if end_line >= start_line:
                label = "Renamed" if current_state else "Unmodified"
                print(f"Lines {start_line}-{end_line}: {label}")
            start_bucket = idx
            current_state = STATE["buckets"][idx]
    start_line = int((start_bucket / BUCKETS) * total_lines) + 1
    if total_lines >= start_line:
        label = "Renamed" if current_state else "Unmodified"
        print(f"Lines {start_line}-{total_lines}: {label}")

def truncate():
    print("Truncating")
    total_lines = len(STATE["lines"])
    if total_lines == 0:
        return
    try:
        choice = input("For truncation enter number of parts to split in: ")
        num_buckets = int(choice)
    except (EOFError, ValueError):
        return
    if num_buckets <= 0:
        return
    truncation_buckets = [False] * num_buckets
    for line_idx in STATE["renamed_lines"]:
        trunc_idx = min(int((line_idx / total_lines) * num_buckets), num_buckets - 1)
        truncation_buckets[trunc_idx] = True
    with open(TRUNCATED_FILE, "w") as f:
        for d in range(num_buckets):
            if truncation_buckets[d]:
                start_line = int((d / num_buckets) * total_lines)
                end_line = int(((d + 1) / num_buckets) * total_lines)
                f.writelines(STATE["lines"][start_line:end_line])
    print(f"Truncated codebase written to {TRUNCATED_FILE}")

if __name__ == "__main__":
    load_source()
    analyze_functions()
    draw_visualization()
    truncate()
    print("Done")
