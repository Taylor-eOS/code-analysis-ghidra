import tkinter as tk
import explore_functions

CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700
DOT_RADIUS = 8
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2
CALLER_X = 150
CALLEE_X = CANVAS_WIDTH - 150
CENTER_COLOR = "#2b7a2b"
CALLER_COLOR = "#4a9a4a"
CALLEE_COLOR = "#4a9a4a"
LINE_COLOR = "#999999"
MAX_SUGGESTIONS = 20

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
    canvas.create_text(x, y + DOT_RADIUS + 10, text=label, font=("TkDefaultFont", 9), tags=(tag,))

def render_center(name):
    VIEW["canvas"].delete("all")
    VIEW["dot_names"] = {}
    VIEW["current_name"] = name
    draw_dot(CENTER_X, CENTER_Y, name, CENTER_COLOR, "center")
    VIEW["dot_names"]["center"] = name
    callers = explore_functions.get_callers(name)
    callees = explore_functions.get_callees(name)
    for i, (x, y) in enumerate(layout_positions(len(callers), CALLER_X, CANVAS_HEIGHT)):
        tag = f"caller{i}"
        VIEW["canvas"].create_line(x, y, CENTER_X, CENTER_Y, fill=LINE_COLOR)
        draw_dot(x, y, callers[i], CALLER_COLOR, tag)
        VIEW["dot_names"][tag] = callers[i]
    for i, (x, y) in enumerate(layout_positions(len(callees), CALLEE_X, CANVAS_HEIGHT)):
        tag = f"callee{i}"
        VIEW["canvas"].create_line(CENTER_X, CENTER_Y, x, y, fill=LINE_COLOR)
        draw_dot(x, y, callees[i], CALLEE_COLOR, tag)
        VIEW["dot_names"][tag] = callees[i]
    entry = explore_functions.STATE["function_map"].get(name)
    if entry is not None:
        VIEW["status_var"].set(f"{name}  |  {len(callers)} callers, {len(callees)} callees  |  {entry['path']}")
    else:
        VIEW["status_var"].set(f"{name}  |  not found in index")

def on_canvas_click(event):
    canvas = VIEW["canvas"]
    items = canvas.find_overlapping(event.x - DOT_RADIUS, event.y - DOT_RADIUS,
                                     event.x + DOT_RADIUS, event.y + DOT_RADIUS)
    for item in items:
        tags = canvas.gettags(item)
        for tag in tags:
            if tag in VIEW["dot_names"]:
                render_center(VIEW["dot_names"][tag])
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
        listbox.insert(tk.END, f"... {total_matches - shown} more, refine search")

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
