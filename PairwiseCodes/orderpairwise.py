
from pathlib import Path
import itertools
import csv
import time
import argparse
import sys
import re
from typing import Tuple, List, Dict

def read_tests_from_file(path: Path) -> List[str]:
    tests = []
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith('#') or s.startswith('//'):
                continue
            tests.append(s)
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for t in tests:
        if t not in seen:
            deduped.append(t)
            seen.add(t)
    return deduped

def split_class_and_method(test_name: str) -> Tuple[str, str]:
    if '#' in test_name:
        class_part, method_part = test_name.rsplit('#', 1)
        return class_part, method_part
    if '.' in test_name:
        class_part, method_part = test_name.rsplit('.', 1)
        return class_part, method_part
    return test_name, 'test'

def class_token_from_index(i: int) -> str:
    if i < 1:
        i = 1
    repeats = (i - 1) // 26 + 1
    letter_index = (i - 1) % 26
    letter = chr(ord('A') + letter_index)
    return letter * repeats

_safe_re = re.compile(r'[^A-Za-z0-9._-]+')
def safe_name(s: str) -> str:
    s = s.replace('/', '.').replace('\\', '.').replace(':', '.')
    s = _safe_re.sub('_', s)
    s = re.sub(r'_{2,}', '_', s).strip('._')
    return s or "item"

def generate_unordered_pairs(items: List[str]):
    yield from itertools.combinations(items, 2)

def build_short_names(originals: List[str]) -> Tuple[List[str], Dict[str, str], Dict[str, Tuple[int, str]]]:
    # First pass: identify class names and assign class indices/tokens
    class_order = []
    class_seen = set()
    class_info: Dict[str, Tuple[int, str]] = {}
    for name in originals:
        cls, _ = split_class_and_method(name)
        if cls not in class_seen:
            class_seen.add(cls)
            class_order.append(cls)
            idx = len(class_order) # 1-based
            class_info[cls] = (idx, class_token_from_index(idx))

    # Second pass: per-class method counters and build short names
    per_class_count: Dict[str, int] = {cls: 0 for cls in class_order}
    mapping: Dict[str, str] = {}
    short_list: List[str] = []

    for name in originals:
        cls, _ = split_class_and_method(name)
        per_class_count[cls] += 1
        method_idx = per_class_count[cls]
        cls_idx, cls_token = class_info[cls]
        short = f"{cls_token}.{method_idx}"
        mapping[name] = short
        short_list.append(short)

    return short_list, mapping, class_info

def write_orders_for_file(input_file: Path, output_root: Path, use_shorten: bool, content_mode: str) -> dict:
    start = time.time()
    originals = read_tests_from_file(input_file)

    out_dir = output_root / input_file.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    if use_shorten:
        short_list, mapping, class_info = build_short_names(originals)
        name_for_file = short_list  # used for pair generation and filenames
        # Persist mapping CSV
        with (out_dir / "mapping.csv").open('w', encoding='utf-8', newline='') as mf:
            w = csv.writer(mf)
            w.writerow(["original", "short"])
            for orig in originals:
                w.writerow([orig, mapping[orig]])
        # Persist normalized (short) list for quick reference
        with (out_dir / "normalized.txt").open('w', encoding='utf-8') as nf:
            for s in short_list:
                nf.write(s + "\n")
        # Persist class mapping
        with (out_dir / "classes.csv").open('w', encoding='utf-8', newline='') as cf:
            w = csv.writer(cf)
            w.writerow(["class_index", "class_name", "class_token"])
            for cls in class_info:
                idx, token = class_info[cls]
                w.writerow([idx, cls, token])
    else:
        mapping = {o: o for o in originals}
        name_for_file = originals

    pairs_idx = list(itertools.combinations(range(len(name_for_file)), 2))
    num_pairs = len(pairs_idx)

    # Determine content mode
    effective_mode = content_mode
    if not use_shorten and content_mode == "short":
        effective_mode = "original"

    width = max(4, len(str(num_pairs)))
    filenames = []
    for idx, (i, j) in enumerate(pairs_idx, start=1):
        if effective_mode == "short":
            t1 = name_for_file[i]
            t2 = name_for_file[j]
        elif effective_mode == "original":
            # map back to originals
            t1 = originals[i]
            t2 = originals[j]
        else:
            # both-with-comments: include originals as comments, write short on two lines
            t1 = name_for_file[i]
            t2 = name_for_file[j]

        # Filename should be short when available for performance/length
        if use_shorten:
            base_fname = f"{safe_name(name_for_file[i])}__{safe_name(name_for_file[j])}"
        else:
            base_fname = f"{safe_name(originals[i])}__{safe_name(originals[j])}"

        fname = f"{str(idx).zfill(width)}_{base_fname}.txt"
        fpath = out_dir / fname
        with fpath.open('w', encoding='utf-8') as f:
            if effective_mode == "short":
                f.write(f"{t1}\n{t2}\n")
            elif effective_mode == "original":
                f.write(f"{t1}\n{t2}\n")
            else:  # both-with-comments
                f.write(f"# ORIGINAL: {originals[i]}\n# ORIGINAL: {originals[j]}\n")
                f.write(f"{t1}\n{t2}\n")

        filenames.append(fname)

    # Write manifest
    manifest_path = out_dir / "manifest.txt"
    with manifest_path.open('w', encoding='utf-8') as mf:
        for name in filenames:
            mf.write(name + "\n")

    duration = time.time() - start
    return {
        "input_file": str(input_file),
        "num_tests": len(originals),
        "num_orders": num_pairs,
        "duration_seconds": round(duration, 6),
        "output_subfolder": str(out_dir),
        "manifest_file": str(manifest_path),
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate UNORDERED pair orders from test name files (with optional shortening).")
    parser.add_argument("--input-dir", required=True, help="Folder with fully-qualified test names (one per line per file).")
    parser.add_argument("--output-dir", default=None, help="Output folder (default: <input-dir>/orders_out)")
    parser.add_argument("--no-shorten-names", action="store_true", help="Disable name shortening (use original names everywhere).")
    parser.add_argument("--content", choices=["original", "short", "both"], default="short",
                        help="What to write inside each order file. Default: short. If --no-shorten-names, coerced to original.")
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"ERROR: --input-dir '{input_dir}' does not exist or is not a directory.", file=sys.stderr)
        return 2

    output_root = Path(args.output_dir) if args.output_dir else (input_dir / "orders_out")
    output_root.mkdir(parents=True, exist_ok=True)

    candidates = [p for p in sorted(input_dir.iterdir()) if p.is_file()]
    if not candidates:
        print(f"No files found in {input_dir}. Nothing to do.")
        return 0

    use_shorten = not args.no_shorten_names
    summary_rows = []
    for file_path in candidates:
        try:
            stats = write_orders_for_file(file_path, output_root, use_shorten, args.content)
            summary_rows.append(stats)
            print(f"Processed: {file_path.name} -> {stats['num_orders']} orders in {stats['duration_seconds']}s")
        except Exception as e:
            print(f"ERROR processing {file_path}: {e}", file=sys.stderr)

    # Write summary CSV
    summary_path = output_root / "summary.csv"
    fieldnames = ["input_file", "num_tests", "num_orders", "duration_seconds", "output_subfolder", "manifest_file"]
    with summary_path.open('w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    print(f"\nSummary written to: {summary_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
