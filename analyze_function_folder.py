from pathlib import Path

def get_files(root_path):
    print("Getting files")
    root_folder = Path(root_path)
    files = []
    for subfolder in sorted(p for p in root_folder.iterdir() if p.is_dir()):
        for p in subfolder.rglob("*"):
            if p.is_file():
                files.append((subfolder.name, p))
    return files

def get_subfolder_file_counts(files):
    counts = {}
    for name, _ in files:
        counts[name] = counts.get(name, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)

def get_largest_files(files, top_n=10):
    sized = [(name, p, p.stat().st_size) for name, p in files]
    sized.sort(key=lambda x: x[2], reverse=True)
    return sized[:top_n]

def get_short_file_count(files):
    count = 0
    for _, p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                if sum(1 for _ in f) < 10:
                    count += 1
        except Exception:
            pass
    return count

def print_subfolder_file_counts(results):
    for name, count in results:
        print(f"{name}: {count}")

def print_largest_files(results):
    for name, p, size in results:
        print(f"{name}/{p.name}: {size} bytes")

def print_short_file_count(count):
    print(f"Files under 10 lines: {count}")

def main():
    files = get_files("rome_functions")
    print("1. Subfolder file counts")
    print("2. Show largest 10 files")
    print("3. Count files under 10 lines")
    choice = input("Select an analysis option: ")
    if choice == "1":
        results = get_subfolder_file_counts(files)
        print_subfolder_file_counts(results)
    elif choice == "2":
        results = get_largest_files(files)
        print_largest_files(results)
    elif choice == "3":
        count = get_short_file_count(files)
        print_short_file_count(count)
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()