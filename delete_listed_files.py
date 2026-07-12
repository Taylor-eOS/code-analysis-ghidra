import os
import sys

STATE = {
    "list_path": "list.txt",
    "base_dir": "rome_functions_cut"
}

def remove_listed_files():
    print(f"Checking list file at: {os.path.abspath(STATE['list_path'])}")
    if not os.path.exists(STATE["list_path"]):
        print("Error: List file does not exist.")
        return
    print(f"Checking target directory at: {os.path.abspath(STATE['base_dir'])}")
    if not os.path.exists(STATE["base_dir"]):
        print("Error: Target directory does not exist.")
        return
    with open(STATE["list_path"], "r") as f:
        lines = f.readlines()
    print(f"Found {len(lines)} lines in the list file.")
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            print("Skipping empty line.")
            continue
        target_path = os.path.join(STATE["base_dir"], cleaned_line)
        print(f"Attempting to delete: {target_path}")
        if os.path.exists(target_path):
            os.remove(target_path)
            print("Status: Success.")
        else:
            print("Status: File not found.")

if __name__ == "__main__":
    remove_listed_files()
