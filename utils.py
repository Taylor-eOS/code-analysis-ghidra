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

def match_definition_before_brace(clean, brace_pos):
    k = brace_pos - 1
    while k >= 0 and clean[k].isspace():
        k -= 1
    if k < 0 or clean[k] != ")":
        return None
    close_paren = k
    paren_pos = matching_paren_open(clean, close_paren, 0)
    if paren_pos is None:
        return None
    k = paren_pos - 1
    while k >= 0 and clean[k].isspace():
        k -= 1
    if k < 0:
        return None
    ident_end = k + 1
    ident_start = ident_end
    while ident_start > 0 and (clean[ident_start - 1].isalnum() or clean[ident_start - 1] == "_"):
        ident_start -= 1
    if ident_start == ident_end:
        return None
    if not (clean[ident_start].isalpha() or clean[ident_start] == "_"):
        return None
    decl_start = clean.rfind("\n", 0, ident_start) + 1
    name = clean[ident_start:ident_end]
    return (name, decl_start)

def matching_paren_open(clean, close_paren_pos, lower_bound):
    depth = 0
    i = close_paren_pos
    while i >= lower_bound:
        if clean[i] == ")":
            depth += 1
        elif clean[i] == "(":
            depth -= 1
            if depth == 0:
                return i
        i -= 1
    return None

def is_column_zero_brace(clean, pos):
    k = pos - 1
    while k >= 0 and clean[k] in " \t":
        k -= 1
    return k < 0 or clean[k] == "\n"

def find_functions(text):
    print("Finding functions")
    clean = strip_comments_and_strings(text)
    n = len(clean)
    functions = []
    i = 0
    while i < n:
        c = clean[i]
        if c == "{" and is_column_zero_brace(clean, i):
            entry = match_definition_before_brace(clean, i)
            close = matching_close(clean, i)
            if close is None:
                break
            if entry is not None:
                name, decl_start = entry
                functions.append((decl_start, close, name))
            i = close + 1
        else:
            i += 1
    return functions
