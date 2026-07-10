import re

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

STRIP_RE = re.compile(
    r'"(?:\\.|[^"\\])*"'
    r"|'(?:\\.|[^'\\])*'"
    r"|//[^\n]*"
    r"|/\*.*?\*/",
    re.DOTALL
)

def _strip_replacement(m):
    matched = m.group(0)
    return "".join(c if c == "\n" else " " for c in matched)

def strip_comments_and_strings(text):
    return STRIP_RE.sub(_strip_replacement, text)

def compute_depths(clean):
    n = len(clean)
    depths = [0] * (n + 1)
    depth = 0
    for i in range(n):
        depths[i] = depth
        if clean[i] == "{":
            depth += 1
        elif clean[i] == "}":
            depth -= 1
    depths[n] = depth
    return depths

def matching_close(clean, open_pos):
    depth = 0
    n = len(clean)
    i = open_pos
    while i < n:
        if clean[i] == "{":
            depth += 1
        elif clean[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None

def matching_paren_close(clean, open_paren_pos):
    depth = 0
    n = len(clean)
    i = open_paren_pos
    while i < n:
        if clean[i] == "(":
            depth += 1
        elif clean[i] == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None

def find_top_level_open_braces(clean):
    n = len(clean)
    depth = 0
    opens = []
    for i in range(n):
        c = clean[i]
        if c == "{":
            if depth == 0:
                opens.append(i)
            depth += 1
        elif c == "}":
            depth -= 1
    return opens

def find_definitions_at_column_zero(clean):
    definitions = []
    n = len(clean)
    for m in re.finditer(r"(?m)^\S", clean):
        line_start = m.start()
        limit = clean.find("{", line_start)
        if limit == -1:
            limit = n
        search_end = min(limit + 1, n)
        j = line_start
        while j < search_end:
            paren_pos = clean.find("(", j, search_end)
            if paren_pos == -1:
                break
            name_match = None
            for match in IDENT_RE.finditer(clean[line_start:paren_pos]):
                name_match = match
            if name_match is not None and name_match.end() + line_start == paren_pos:
                close_paren = matching_paren_close(clean, paren_pos)
                if close_paren is not None:
                    k = close_paren + 1
                    while k < n and clean[k].isspace():
                        k += 1
                    if k < n and clean[k] == "{":
                        name = name_match.group(0)
                        definitions.append((name, line_start, k))
                        break
            j = paren_pos + 1
    return definitions

def find_functions(text):
    clean = strip_comments_and_strings(text)
    defs = find_definitions_at_column_zero(clean)
    all_top_braces = find_top_level_open_braces(clean)
    brace_to_def = {fbrace: (fname, fstart) for fname, fstart, fbrace in defs}
    functions = []
    for brace_pos in all_top_braces:
        entry = brace_to_def.get(brace_pos)
        close_pos = matching_close(clean, brace_pos)
        if close_pos is None:
            break
        if entry is not None:
            name, decl_start = entry
            functions.append((decl_start, close_pos, name))
    return functions
