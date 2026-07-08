

def find_function_boundaries(lines):
    boundaries = []
    for i, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        idx = line.find("FUN_")
        if idx == -1 or "(" not in line or "=" in line or ";" in line:
            continue
        name_end = line.find("(", idx)
        name = line[idx:name_end].strip()
        if len(name) > 12:
            boundaries.append(i)
    return boundaries
