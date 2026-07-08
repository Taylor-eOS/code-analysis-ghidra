import subprocess

STATE = {
    "file_name": "Rome.c",
    "output_name": "lines_around.txt",
    "line_numbers": [],
    "file_lines": []
}
SEARCH_TERMS = ["  uVar1 = (**(code **)(*param_9 + 0x1c0))();"]
INCLUDE_LINE_NUMBERS = False
LINES_BEFORE = 120
LINES_AFTER = 120

def load_file():
    with open(STATE["file_name"], "r", encoding="utf-8", errors="ignore") as f:
        STATE["file_lines"] = f.readlines()

def execute_grep():
    if not SEARCH_TERMS:
        return
    for index, line in enumerate(STATE["file_lines"]):
        match = True
        for term in SEARCH_TERMS:
            if term not in line:
                match = False
                break
        if match:
            STATE["line_numbers"].append(index + 1)

def save_results():
    with open(STATE["output_name"], "w", encoding="utf-8") as f:
        total_matches = len(STATE["line_numbers"])
        print(f"Found {total_matches} results")
        for index, line_num in enumerate(STATE["line_numbers"]):
            if INCLUDE_LINE_NUMBERS:
                f.write(f"{line_num}:\n")
            f.write("```\n")
            start_idx = max(0, line_num - 1 - LINES_BEFORE)
            end_idx = min(len(STATE["file_lines"]), line_num + LINES_AFTER)
            for i in range(start_idx, end_idx):
                f.write(STATE["file_lines"][i])
            f.write("```\n")
            if index < total_matches - 1:
                f.write("\n")

if __name__ == "__main__":
    load_file()
    execute_grep()
    save_results()
    print("Done")

