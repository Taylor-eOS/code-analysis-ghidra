import sys
import explore_functions

SEED_FILE = "list.txt"
OUTPUT_FILE = "related_functions.txt"
RESTART_PROB = 0.15
NUM_ITERATIONS = 30
BACKWARD_WEIGHT = 0.7
FORWARD_WEIGHT = 0.3
TOP_N = 300

def load_seeds(path):
    print("Loading list")
    with open(path, "r") as f:
        names = [line.strip() for line in f if line.strip()]
    known = []
    unknown = []
    for name in names:
        if name in explore_functions.STATE["function_map"]:
            known.append(name)
        elif name.startswith("FUN_") and len(name) > 12 and name[12] == "_":
            base = name[:12]
            if base in explore_functions.STATE["function_map"]:
                known.append(base)
            else:
                unknown.append(name)
        else:
            found = None
            for key in explore_functions.STATE["function_map"]:
                if key.startswith("FUN_") and len(key) > 12 and key[12] == "_" and key[:12] == name:
                    found = key
                    break
            if found is not None:
                known.append(found)
            else:
                unknown.append(name)
    return known, unknown

def personalized_pagerank(seeds, get_neighbors):
    seed_set = set(seeds)
    all_nodes = set(explore_functions.STATE["function_map"].keys())
    restart_mass = 1.0 / len(seed_set)
    scores = {node: (restart_mass if node in seed_set else 0.0) for node in all_nodes}
    for _ in range(NUM_ITERATIONS):
        new_scores = {node: 0.0 for node in all_nodes}
        for node, score in scores.items():
            if score == 0.0:
                continue
            neighbors = get_neighbors(node)
            if not neighbors:
                continue
            share = score * (1.0 - RESTART_PROB) / len(neighbors)
            for neighbor in neighbors:
                if neighbor in new_scores:
                    new_scores[neighbor] += share
        for node in seed_set:
            new_scores[node] += RESTART_PROB * restart_mass
        scores = new_scores
    return scores

def backward_neighbors(name):
    return explore_functions.get_callers(name)

def forward_neighbors(name):
    return explore_functions.get_callees(name)

def main():
    explore_functions.index_all_functions()
    seeds, unknown = load_seeds(SEED_FILE)
    if unknown:
        print(f"Warning: {len(unknown)} listed names not found in index:")
        for name in unknown:
            print(f"  {name}")
    if not seeds:
        print("No valid list found, aborting")
        sys.exit(1)
    print(f"Running diffusion from {len(seeds)} listed functions")
    backward_scores = personalized_pagerank(seeds, backward_neighbors)
    forward_scores = personalized_pagerank(seeds, forward_neighbors)
    seed_set = set(seeds)
    combined = []
    for name in explore_functions.STATE["function_map"]:
        if name in seed_set:
            continue
        b = backward_scores.get(name, 0.0)
        f = forward_scores.get(name, 0.0)
        total = BACKWARD_WEIGHT * b + FORWARD_WEIGHT * f
        if total > 0.0:
            combined.append((total, b, f, name))
    combined.sort(key=lambda entry: entry[0], reverse=True)
    with open(OUTPUT_FILE, "w") as out:
        out.write(f"Listed ({len(seeds)}):\n")
        for name in seeds:
            out.write(f"  {name}\n")
        out.write("\n")
        out.write(f"Top {min(TOP_N, len(combined))} related functions (backward weight {BACKWARD_WEIGHT}, forward weight {FORWARD_WEIGHT}):\n\n")
        for total, b, f, name in combined[:TOP_N]:
            entry = explore_functions.STATE["function_map"][name]
            out.write(f"{total:.6f}  (back {b:.6f}, fwd {f:.6f})  {name}\n")
            out.write(f"    {entry['signature']}\n")
            out.write(f"    {entry['path']}\n")
    print(f"Wrote {min(TOP_N, len(combined))} results to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
