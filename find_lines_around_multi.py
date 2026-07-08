import os

STATE = {
    "file_name": "Rome.c",
    "output_name": "lines_around.txt",
    "file_lines": [],
    "matches": []
}
SEARCH_TERMS = ["FUN_0127d300_postbattleresultsaggregation", "param_9"]
INCLUDE_LINE_NUMBERS = False
SEARCH_WINDOW = 6
LINES_AROUND = 100
MERGE_OVERLAPPING = True

def load_file():
    with open(STATE["file_name"], "r", encoding="utf-8", errors="ignore") as f:
        STATE["file_lines"] = f.readlines()

def execute_search():
    lines = STATE["file_lines"]
    raw_matches = []
    for i in range(len(lines)):
        search_start = max(0, i - SEARCH_WINDOW)
        search_end = min(len(lines), i + SEARCH_WINDOW + 1)
        block = "".join(lines[search_start:search_end])
        if all(term in block for term in SEARCH_TERMS):
            print_start = max(0, i - LINES_AROUND)
            print_end = min(len(lines), i + LINES_AROUND + 1)
            raw_matches.append((print_start, print_end))
    if not MERGE_OVERLAPPING:
        STATE["matches"] = raw_matches
        return
    merged = []
    for start, end in raw_matches:
        if not merged:
            merged.append([start, end])
            continue
        if start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1][1] = end
        else:
            merged.append([start, end])
    STATE["matches"] = [(a, b) for a, b in merged]

def save_results():
    with open(STATE["output_name"], "w", encoding="utf-8") as f:
        print(f"Found {len(STATE['matches'])} matching regions")
        for index, (start, end) in enumerate(STATE["matches"]):
            f.write("```\n")
            for line_num in range(start, end):
                if INCLUDE_LINE_NUMBERS:
                    f.write(f"{line_num + 1}: ")
                f.write(STATE["file_lines"][line_num])
            f.write("```\n")
            if index < len(STATE["matches"]) - 1:
                f.write("\n")

if __name__ == "__main__":
    if not os.path.exists(STATE["file_name"]):
        print(f"File not found: {STATE['file_name']}")
    else:
        load_file()
        execute_search()
        save_results()
        print("Done")
