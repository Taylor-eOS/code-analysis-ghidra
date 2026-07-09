import subprocess
import tkinter as tk
import explore_functions
from gguf_llm_library import ask_llm

CANVAS_WIDTH = 1400
CANVAS_HEIGHT = 700
DOT_RADIUS = 4
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2
CENTER_COLOR = "#2b7a2b"
CALLER_COLOR = "#4a9a4a"
CALLEE_COLOR = "#4a9a4a"
MORE_COLOR = "#bbbbbb"
LINE_COLOR = "#999999"
MAX_SUGGESTIONS = 22
MAX_DEPTH = 5
MAX_PER_COLUMN = 12
COLUMN_GAP = (CANVAS_WIDTH // 2 - 40) // MAX_DEPTH

VIEW = {"root": None, "name_entry": None, "suggest_list": None, "canvas": None,
        "status_var": None, "current_name": None, "dot_names": {}, "sorted_names": []}

def layout_positions(count, x, height):
    if count == 0:
        return []
    spacing = height / (count + 1)
    return [(x, int(spacing * (i + 1))) for i in range(count)]

def draw_dot(x, y, label, color, tag):
    canvas = VIEW["canvas"]
    canvas.create_oval(x - DOT_RADIUS, y - DOT_RADIUS, x + DOT_RADIUS, y + DOT_RADIUS,
                        fill=color, outline="black", tags=(tag,))
    canvas.create_text(x, y + DOT_RADIUS + 8, text=label, font=("TkDefaultFont", 7), tags=(tag,))

def build_chain(name, direction, max_depth):
    """Walk the call graph outward from `name` in one direction ('callers' or 'callees'),
    up to max_depth hops. Returns a list of columns; each column is a dict:
    {"names": [...capped names...], "truncated": int, "parent_of": {name: [parent names in prev column]}}
    Duplicate names within a column are merged (kept once). Already-visited names
    (anywhere in the chain so far) are not expanded further, to avoid cycles/recursion blowups.
    """
    get_next = explore_functions.get_callers if direction == "callers" else explore_functions.get_callees
    columns = []
    visited = {name}
    frontier = [name]
    for depth in range(max_depth):
        next_names_ordered = []
        seen_this_depth = set()
        parent_of = {}
        for parent in frontier:
            try:
                neighbors = get_next(parent) or []
            except Exception:
                neighbors = []
            for n in neighbors:
                if n not in seen_this_depth:
                    seen_this_depth.add(n)
                    next_names_ordered.append(n)
                parent_of.setdefault(n, [])
                if parent not in parent_of[n]:
                    parent_of[n].append(parent)
        if not next_names_ordered:
            break
        total = len(next_names_ordered)
        shown = next_names_ordered[:MAX_PER_COLUMN]
        truncated = total - len(shown)
        columns.append({"names": shown, "truncated": truncated, "parent_of": parent_of})
        new_frontier = [n for n in shown if n not in visited]
        visited.update(shown)
        if not new_frontier:
            break
        frontier = new_frontier
    return columns

def render_center(name):
    VIEW["canvas"].delete("all")
    VIEW["dot_names"] = {}
    VIEW["current_name"] = name
    draw_dot(CENTER_X, CENTER_Y, name, CENTER_COLOR, "center")
    VIEW["dot_names"]["center"] = name

    caller_columns = build_chain(name, "callers", MAX_DEPTH)
    callee_columns = build_chain(name, "callees", MAX_DEPTH)

    _render_side(caller_columns, direction="callers")
    _render_side(callee_columns, direction="callees")

    entry = explore_functions.STATE["function_map"].get(name)
    n_callers = len(caller_columns[0]["names"]) if caller_columns else 0
    n_callees = len(callee_columns[0]["names"]) if callee_columns else 0
    if entry is not None:
        VIEW["status_var"].set(
            f"{name}  |  {n_callers} direct callers, {n_callees} direct callees  |  "
            f"chain depth {len(caller_columns)} back / {len(callee_columns)} forward  |  {entry['path']}")
    else:
        VIEW["status_var"].set(f"{name}  |  not found in index")

def _render_side(columns, direction):
    """Draw one side (callers = left, callees = right) of the chain.
    columns[0] is one hop away from center, columns[1] is two hops away, etc.
    Each node's position is tracked so lines can connect it to its parent(s)
    in the previous column (or to center, for column 0).
    """
    canvas = VIEW["canvas"]
    color = CALLER_COLOR if direction == "callers" else CALLEE_COLOR
    sign = -1 if direction == "callers" else 1

    # positions[col_index][name] = (x, y), where col_index -1 means the center node
    positions = {-1: {None: (CENTER_X, CENTER_Y)}}

    for col_index, col in enumerate(columns):
        x = CENTER_X + sign * COLUMN_GAP * (col_index + 1)
        names = col["names"]
        truncated = col["truncated"]
        slots = len(names) + (1 if truncated else 0)
        coords = layout_positions(slots, x, CANVAS_HEIGHT)
        positions[col_index] = {}

        prev_positions = positions[col_index - 1]
        for i, node_name in enumerate(names):
            nx, ny = coords[i]
            positions[col_index][node_name] = (nx, ny)
            parents = col["parent_of"].get(node_name, [])
            if col_index == 0:
                px, py = prev_positions[None]
                canvas.create_line(px, py, nx, ny, fill=LINE_COLOR)
            else:
                for parent in parents:
                    if parent in prev_positions:
                        px, py = prev_positions[parent]
                        canvas.create_line(px, py, nx, ny, fill=LINE_COLOR)
            tag = f"{direction}{col_index}_{i}"
            draw_dot(nx, ny, node_name, color, tag)
            VIEW["dot_names"][tag] = node_name

        if truncated:
            mx, my = coords[-1]
            tag = f"{direction}{col_index}_more"
            label = f"+{truncated} more..."
            canvas.create_text(mx, my, text=label, font=("TkDefaultFont", 7), fill=MORE_COLOR, tags=(tag,))
            # not clickable / not added to dot_names since it isn't a real function name

def copy_name_to_clipboard(name):
    VIEW["root"].clipboard_clear()
    VIEW["root"].clipboard_append(name)
    entry = explore_functions.STATE["function_map"].get(name)
    if entry is not None:
        VIEW["status_var"].set(f"Copied '{name}' to clipboard  |  {entry['path']}")
    else:
        VIEW["status_var"].set(f"Copied '{name}' to clipboard  |  not found in index")

def open_current_file():
    name = VIEW["current_name"]
    if name is None:
        return
    entry = explore_functions.STATE["function_map"].get(name)
    if entry is None:
        VIEW["status_var"].set(f"{name}  |  not found in index")
        return
    subprocess.Popen(["xdg-open", entry["path"]])

def summarize_current_file():
    name = VIEW["current_name"]
    if name is None:
        return
    entry = explore_functions.STATE["function_map"].get(name)
    if entry is None:
        VIEW["status_var"].set(f"{name}  |  not found in index")
        return
    try:
        with open(entry["path"], "r") as f:
            code = f.read()
    except OSError as exc:
        VIEW["status_var"].set(f"Could not read {entry['path']}: {exc}")
        return
    VIEW["status_var"].set(f"Asking LLM to summarize {entry['path']}...")
    VIEW["root"].update_idletasks()
    prompt = f"{code}\n\nInstruction: Describe the functions specific role in the games internal logic by identifying what unique operation it performs compared to other functions. Focus on the concrete behavior visible in the code. Summarize this as one plain sentence that states the functions distinct purpose rather than a generic category. All functions are from the Rome Total War source code, that does not have to be mentioned. Do not invent specifics that you can't know. Write your response as one single unformatted sentence."
    try:
        summary = ask_llm(prompt, 3)
    except Exception as exc:
        VIEW["status_var"].set(f"LLM error: {exc}")
        return
    print(summary)
    VIEW["status_var"].set(f"{summary}")

def on_canvas_click(event):
    canvas = VIEW["canvas"]
    hit_radius = DOT_RADIUS + 4
    items = canvas.find_overlapping(event.x - hit_radius, event.y - hit_radius, event.x + hit_radius, event.y + hit_radius)
    for item in items:
        tags = canvas.gettags(item)
        for tag in tags:
            if tag in VIEW["dot_names"]:
                clicked_name = VIEW["dot_names"][tag]
                if tag == "center":
                    copy_name_to_clipboard(clicked_name)
                else:
                    render_center(clicked_name)
                return

def update_suggestions():
    query = VIEW["name_entry"].get().strip().lower()
    listbox = VIEW["suggest_list"]
    listbox.delete(0, tk.END)
    if query == "":
        return
    shown = 0
    total_matches = 0
    for name in VIEW["sorted_names"]:
        if query in name.lower():
            total_matches += 1
            if shown < MAX_SUGGESTIONS:
                listbox.insert(tk.END, name)
                shown += 1
    if total_matches > shown:
        listbox.insert(tk.END, f"{total_matches - shown} more...")

def on_entry_key_release(event=None):
    if event is not None and event.keysym == "Return":
        return
    update_suggestions()

def on_entry_submit(event=None):
    query = VIEW["name_entry"].get().strip()
    if query == "":
        return
    if query in explore_functions.STATE["function_map"]:
        render_center(query)
        return
    listbox = VIEW["suggest_list"]
    if listbox.size() > 0:
        first = listbox.get(0)
        if first in explore_functions.STATE["function_map"]:
            render_center(first)
            return
    render_center(query)

def on_suggest_select(event):
    selection = VIEW["suggest_list"].curselection()
    if not selection:
        return
    name = VIEW["suggest_list"].get(selection[0])
    if name in explore_functions.STATE["function_map"]:
        render_center(name)

def build_ui():
    root = tk.Tk()
    root.title("Function Call Map")
    VIEW["root"] = root
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)
    tk.Label(top_frame, text="Function name:").pack(side=tk.LEFT)
    name_entry = tk.Entry(top_frame, width=40)
    name_entry.pack(side=tk.LEFT, padx=4)
    name_entry.bind("<Return>", on_entry_submit)
    name_entry.bind("<KeyRelease>", on_entry_key_release)
    VIEW["name_entry"] = name_entry
    tk.Button(top_frame, text="Show", command=on_entry_submit).pack(side=tk.LEFT, padx=4)
    tk.Button(top_frame, text="Open file", command=open_current_file).pack(side=tk.LEFT, padx=4)
    tk.Button(top_frame, text="Summarize file", command=summarize_current_file).pack(side=tk.LEFT, padx=4)
    body_frame = tk.Frame(root)
    body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    suggest_list = tk.Listbox(body_frame, width=40)
    suggest_list.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
    suggest_list.bind("<<ListboxSelect>>", on_suggest_select)
    VIEW["suggest_list"] = suggest_list
    canvas = tk.Canvas(body_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)
    canvas.bind("<Button-1>", on_canvas_click)
    VIEW["canvas"] = canvas
    status_var = tk.StringVar()
    status_var.set("Type a function name and press Enter, or pick a suggestion")
    VIEW["status_var"] = status_var
    tk.Label(root, textvariable=status_var, anchor="w").pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)
    return root

def main():
    explore_functions.index_all_functions()
    VIEW["sorted_names"] = sorted(explore_functions.STATE["function_map"])
    count = len(explore_functions.STATE["function_map"])
    folders = len(explore_functions.STATE["folders"])
    print(f"Indexed {count} functions across {folders} folders (ROOT_DIR={explore_functions.ROOT_DIR!r}, cwd={__import__('os').getcwd()!r})")
    root = build_ui()
    root.mainloop()

if __name__ == "__main__":
    main()
