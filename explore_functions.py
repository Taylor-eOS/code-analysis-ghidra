import os

ROOT_DIR = "rome_functions_test"
STATE = {"folders": [], "current_file": None, "current_lines": None, "functions": [], "function_map": {}, "caller_map": {}}
C_KEYWORDS = {
    "if", "else", "while", "for", "do", "switch", "case", "default",
    "return", "sizeof", "goto", "break", "continue", "typedef",
    "struct", "union", "enum", "static", "extern", "const", "volatile",
    "register", "inline", "void", "signed", "unsigned",
}

def strip_comments_and_literals(text):
    result = []
    length = len(text)
    pos = 0
    while pos < length:
        c = text[pos]
        if c == "/" and pos + 1 < length and text[pos + 1] == "/":
            end = text.find("\n", pos)
            if end == -1:
                pos = length
            else:
                result.append("\n")
                pos = end + 1
            continue
        if c == "/" and pos + 1 < length and text[pos + 1] == "*":
            end = text.find("*/", pos + 2)
            span = text[pos:length] if end == -1 else text[pos:end + 2]
            result.append("".join("\n" if ch == "\n" else " " for ch in span))
            pos = length if end == -1 else end + 2
            continue
        if c == '"' or c == "'":
            quote = c
            j = pos + 1
            while j < length:
                if text[j] == "\\" and j + 1 < length:
                    j += 2
                    continue
                if text[j] == quote:
                    j += 1
                    break
                j += 1
            span = text[pos:j]
            result.append("".join("\n" if ch == "\n" else " " for ch in span))
            pos = j
            continue
        result.append(c)
        pos += 1
    return "".join(result)

def is_identifier_char(c):
    return c.isalnum() or c == "_"

def is_identifier_start(c):
    return c.isalpha() or c == "_"

def find_matching_close(text, open_pos, open_char, close_char):
    pos = open_pos
    length = len(text)
    depth = 0
    while pos < length:
        c = text[pos]
        if c == open_char:
            depth += 1
        elif c == close_char:
            depth -= 1
            if depth == 0:
                return pos
        pos += 1
    return None

def scan_identifiers(text, start, end):
    occurrences = []
    pos = start
    while pos < end:
        c = text[pos]
        if is_identifier_start(c):
            begin = pos
            pos += 1
            while pos < end and is_identifier_char(text[pos]):
                pos += 1
            occurrences.append((begin, pos, text[begin:pos]))
        else:
            pos += 1
    return occurrences

def next_non_space(text, pos, length):
    while pos < length and text[pos] in " \t\r\n":
        pos += 1
    return pos

def split_top_level_commas(text):
    parts = []
    depth = 0
    current_start = 0
    pos = 0
    length = len(text)
    while pos < length:
        c = text[pos]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(text[current_start:pos])
            current_start = pos + 1
        pos += 1
    parts.append(text[current_start:length])
    return parts

def parse_argument_list(args_text):
    args_text = args_text.strip()
    if args_text == "" or args_text == "void":
        return []
    raw_parts = split_top_level_commas(args_text)
    args = []
    for part in raw_parts:
        cleaned = " ".join(part.split())
        if cleaned != "":
            args.append(cleaned)
    return args

def find_function_definitions(clean_text):
    length = len(clean_text)
    definitions = []
    pos = 0
    depth = 0
    while pos < length:
        c = clean_text[pos]
        if c == "{":
            if depth == 0:
                open_paren_pos = clean_text.rfind("(", 0, pos)
                if open_paren_pos != -1:
                    close_paren_pos = find_matching_close(clean_text, open_paren_pos, "(", ")")
                    if close_paren_pos is not None:
                        gap = next_non_space(clean_text, close_paren_pos + 1, length)
                        if gap == pos:
                            name_end = open_paren_pos
                            while name_end > 0 and clean_text[name_end - 1] in " \t\r\n":
                                name_end -= 1
                            name_start = name_end
                            while name_start > 0 and is_identifier_char(clean_text[name_start - 1]):
                                name_start -= 1
                            if name_start < name_end and is_identifier_start(clean_text[name_start]) and clean_text[name_start:name_end] not in C_KEYWORDS:
                                name = clean_text[name_start:name_end]
                                sig_start = clean_text.rfind("\n", 0, name_start)
                                sig_start = 0 if sig_start == -1 else sig_start + 1
                                sig_start = next_non_space(clean_text, sig_start, length)
                                body_end = find_matching_close(clean_text, pos, "{", "}")
                                if body_end is not None:
                                    definitions.append({
                                        "name": name,
                                        "name_start": name_start,
                                        "sig_start": sig_start,
                                        "args_start": open_paren_pos,
                                        "args_end": close_paren_pos,
                                        "body_start": pos,
                                        "body_end": body_end,
                                    })
            depth += 1
        elif c == "}":
            if depth > 0:
                depth -= 1
        pos += 1
    return definitions

def extract_calls(clean_text, body_start, body_end):
    calls = []
    for name_start, name_end, name in scan_identifiers(clean_text, body_start, body_end):
        if name in C_KEYWORDS:
            continue
        after = next_non_space(clean_text, name_end, len(clean_text))
        if after < len(clean_text) and clean_text[after] == "(":
            calls.append(name)
    return calls

def extract_function_identifiers(lines):
    raw_text = "".join(lines)
    clean_text = strip_comments_and_literals(raw_text)
    definitions = find_function_definitions(clean_text)
    results = []
    for definition in definitions:
        args_text = clean_text[definition["args_start"] + 1:definition["args_end"]]
        args = parse_argument_list(args_text)
        signature = clean_text[definition["sig_start"]:definition["args_end"] + 1]
        signature = " ".join(signature.split())
        calls = extract_calls(clean_text, definition["body_start"] + 1, definition["body_end"])
        line_idx = clean_text.count("\n", 0, definition["name_start"])
        results.append({
            "name": definition["name"],
            "line": line_idx,
            "args": args,
            "signature": signature,
            "calls": calls,
        })
    return results

def list_folders():
    STATE["folders"] = sorted(d for d in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, d)))

def list_files(folder):
    folder_path = os.path.join(ROOT_DIR, folder)
    return sorted(f for f in os.listdir(folder_path) if f.endswith(".c"))

def load_file(filename):
    path = os.path.join(ROOT_DIR, filename[4:7], filename)
    with open(path, "r") as f:
        STATE["current_lines"] = f.readlines()
    STATE["current_file"] = path

def detect_functions():
    definitions = extract_function_identifiers(STATE["current_lines"])
    STATE["functions"] = definitions
    for definition in definitions:
        entry = {
            "path": STATE["current_file"],
            "name": definition["name"],
            "line": definition["line"],
            "args": definition["args"],
            "signature": definition["signature"],
            "calls": definition["calls"],
        }
        STATE["function_map"][definition["name"]] = entry
    return definitions

def build_caller_map():
    STATE["caller_map"] = {}
    for name, entry in STATE["function_map"].items():
        for callee in entry["calls"]:
            STATE["caller_map"].setdefault(callee, set()).add(name)

def index_all_functions():
    list_folders()
    for folder in STATE["folders"]:
        for filename in list_files(folder):
            load_file(filename)
            detect_functions()
    build_caller_map()

def get_callees(name):
    entry = STATE["function_map"].get(name)
    if entry is None:
        return []
    seen = set()
    result = []
    for callee in entry["calls"]:
        if callee not in seen:
            seen.add(callee)
            result.append(callee)
    return result

def get_callers(name):
    return sorted(STATE["caller_map"].get(name, ()))

def search_function_names(query, limit=50):
    query = query.lower()
    matches = []
    for name in STATE["function_map"]:
        if query in name.lower():
            matches.append(name)
            if len(matches) >= limit:
                break
    return sorted(matches)

def main():
    index_all_functions()
    print(f"Indexed {len(STATE['function_map'])} functions across {len(STATE['folders'])} folders")

if __name__ == "__main__":
    main()
