#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Optional, Tuple

OUTPUT_DIR_NAME = "simplified_original_test_orders"

def make_class_label(idx: int) -> str:
    if idx < 1:
        raise ValueError("Index must be 1-based and positive")
    letter = chr(ord('A') + (idx - 1) % 26)
    repeats = 1 + (idx - 1) // 26
    # Compress repeats: A, B, ..., Z, then A2, B2, ..., Z2, then A3, ...
    return letter if repeats == 1 else f"{letter}{repeats}"

def parse_line(line: str) -> Optional[Tuple[str, str]]:
    s = line.strip()
    if not s:
        return None
    s = re.sub(r"\(.*\)$", "", s)  # strip parameters like "()"
    parts = s.split(".")
    if len(parts) < 2:
        return (s, "1")
    test_name = parts[-1]
    class_part = parts[-2]
    class_name = class_part.split("$")[0] if "$" in class_part else class_part
    return (class_name, test_name)

def simplify_stream(lines):
    """Yield simplified lines given an iterable of raw text lines (per file)."""
    class_to_label = {}
    class_order = []
    per_class_counts = {}

    for raw in lines:
        parsed = parse_line(raw)
        if not parsed:
            continue
        cls, _ = parsed
        if cls not in class_to_label:
            class_order.append(cls)
            label = make_class_label(len(class_order))
            class_to_label[cls] = label
            per_class_counts[cls] = 0
        per_class_counts[cls] += 1
        yield f"{class_to_label[cls]}.{per_class_counts[cls]}"

def simplify_file(input_path: Path, output_path: Path) -> None:
    # Read as text, be forgiving with encoding
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        simplified = list(simplify_stream(f))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("\n".join(simplified))

def main():
    try:
        input_path_str = input("Enter the path to the FOLDER containing files to simplify: ").strip()
    except EOFError:
        print("No input received. Exiting.")
        return
    if not input_path_str:
        print("Empty path provided. Exiting.")
        return

    inpath = Path(input_path_str).expanduser().resolve()
    if not inpath.exists():
        print(f"Path not found: {inpath}")
        return
    if not inpath.is_dir():
        print(f"Provided path is not a folder: {inpath}")
        return

    # Determine where to place outputs (next to this script)
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        # Fallback if __file__ is not defined (e.g., interactive run)
        script_dir = Path.cwd()

    outdir = script_dir / OUTPUT_DIR_NAME
    outdir.mkdir(parents=True, exist_ok=True)

    # Process each regular file in the top level of the folder (non-recursive)
    files = [p for p in inpath.iterdir() if p.is_file()]
    if not files:
        print(f"No files found in folder: {inpath}")
        print(f"Output folder created (empty): {outdir}")
        return

    processed = 0
    skipped = 0
    for infile in sorted(files):
        # Create matching output filename (same name & extension) in the output dir
        outfile = outdir / infile.name
        try:
            simplify_file(infile, outfile)
            print(f"Simplified: {infile.name} -> {outfile}")
            processed += 1
        except Exception as e:
            print(f"Skipped (error reading or writing): {infile} ({e})")
            skipped += 1

    print("\n=== Summary ===")
    print(f"Input folder: {inpath}")
    print(f"Output folder: {outdir}")
    print(f"Files processed: {processed}")
    print(f"Files skipped:   {skipped}")

if __name__ == "__main__":
    main()
