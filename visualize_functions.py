SOURCE_FILE = "Rome.c"
TRUNCATED_FILE = "Rome_truncated.c"
BUCKETS = 100
STATE = {"lines": None, "buckets": [False] * BUCKETS, "renamed_lines": []}

def load_source():
    print("Loading source")
    with open(SOURCE_FILE, "r") as f:
        STATE["lines"] = f.readlines()

def analyze_functions():
    print("Analyzing functions")
    lines = STATE["lines"]
    total_lines = len(lines)
    if total_lines == 0:
        return
    for i, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        idx = line.find("FUN_")
        if idx == -1 or "(" not in line or "=" in line or ";" in line:
            continue
        name_end = line.find("(", idx)
        name = line[idx:name_end].strip()
        if len(name) > 12:
            bucket_idx = min(int((i / total_lines) * BUCKETS), BUCKETS - 1)
            STATE["buckets"][bucket_idx] = True
            STATE["renamed_lines"].append(i)

def draw_visualization():
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

def main():
    load_source()
    analyze_functions()
    draw_visualization()
    truncate()

if __name__ == "__main__":
    main()
