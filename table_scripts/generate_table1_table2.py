#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = Path(__file__).resolve().parent


def read_csv_rows(path: Path) -> List[List[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def write_csv_rows(path: Path, rows: Iterable[Iterable[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def parse_number(value: str) -> Optional[float]:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def format_int(value: Optional[int]) -> str:
    if value is None:
        return ""
    return f"{value:,}"


def format_float(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def module_name_from_path(module: str, project: str) -> str:
    if module == ".":
        return project.split("/")[-1]
    return Path(module).name


def original_order_filename(project: str, sha: str, module: str) -> str:
    cproject = project.replace("/", "_")
    cmodule = module.replace("/", "_")
    return f"{cproject}-{cmodule}-{sha[:7]}-original_order"


def read_tests(path: Path) -> List[str]:
    with path.open(encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


def class_name(test_name: str) -> str:
    if "#" in test_name:
        return test_name.rsplit("#", 1)[0]
    if "." in test_name:
        return test_name.rsplit(".", 1)[0]
    return test_name


def count_rounds_and_tests(module_dir: Path) -> Tuple[Optional[int], Optional[int]]:
    if not module_dir.is_dir():
        return None, None
    orders = 0
    tests = 0
    for path in sorted(module_dir.glob("round*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            order = data.get("testOrder", [])
        except Exception:
            continue
        if isinstance(order, list):
            orders += 1
            tests += len(order)
    return orders, tests


def load_static_table1(path: Path) -> Dict[str, Dict[str, str]]:
    rows = read_csv_rows(path)
    if len(rows) < 2:
        return {}
    header = rows[1]
    out: Dict[str, Dict[str, str]] = {}
    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        values = {header[i]: row[i] if i < len(row) else "" for i in range(len(header))}
        out[values["Module"]] = values
    return out


def load_static_table2(path: Path) -> Dict[str, Dict[str, str]]:
    rows = read_csv_rows(path)
    if len(rows) < 2:
        return {}
    out: Dict[str, Dict[str, str]] = {}
    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        out[row[0]] = {
            "prior_orders": row[1] if len(row) > 1 else "",
            "prior_tests": row[4] if len(row) > 4 else "",
            "prior_time": row[7] if len(row) > 7 else "",
            "pairwise_time": row[8] if len(row) > 8 else "",
            "tuscane_time": row[9] if len(row) > 9 else "",
        }
    return out


def load_timing_csv(path: Path) -> Dict[str, float]:
    timings: Dict[str, float] = {}
    if not path.is_file():
        return timings
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 5:
                continue
            seconds = parse_number(row[-1])
            if seconds is None:
                continue
            module = module_name_from_path(row[2], row[0])
            timings[module] = seconds
    return timings


def load_pairwise_summary(path: Path) -> Dict[str, Dict[str, float]]:
    summary: Dict[str, Dict[str, float]] = {}
    if not path.is_file():
        return summary
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out_folder = row.get("output_subfolder", "")
            module = Path(out_folder).name if out_folder else Path(row.get("input_file", "")).stem
            orders = parse_number(row.get("num_orders", ""))
            tests = parse_number(row.get("num_tests", ""))
            duration = parse_number(row.get("duration_seconds", ""))
            summary[module] = {
                "orders": orders if orders is not None else 0,
                "tests": tests if tests is not None else 0,
                "duration": duration if duration is not None else 0,
            }
    return summary


def load_tuscanic_summary(path: Path) -> Dict[str, Dict[str, float]]:
    if not path.is_file():
        return {}
    out: Dict[str, Dict[str, float]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            module = row.get("module") or row.get("Module") or row.get("output_subfolder", "")
            module = Path(module).name
            if not module:
                continue
            out[module] = {
                "orders": parse_number(row.get("num_orders", "")) or 0,
                "tests_run": parse_number(row.get("num_tests_run", "")) or 0,
                "duration": parse_number(row.get("duration_seconds", "")) or 0,
            }
    return out


def build_module_records(modules_csv: Path, original_orders_dir: Path) -> List[Dict[str, object]]:
    rows = read_csv_rows(modules_csv)
    records: List[Dict[str, object]] = []
    for row in rows:
        if len(row) < 3 or row[0] == "Project":
            continue
        project, sha, module = row[0], row[1], row[2]
        module_name = module_name_from_path(module, project)
        original_file = original_orders_dir / original_order_filename(project, sha, module)
        tests = read_tests(original_file) if original_file.is_file() else []
        records.append(
            {
                "project": project,
                "sha": sha,
                "module_path": module,
                "module": module_name,
                "tests": len(tests),
                "classes": len({class_name(t) for t in tests}),
            }
        )
    return records


def add_average_row(rows: List[List[str]], numeric_start: int, label_col: int) -> None:
    if len(rows) <= 2:
        return
    width = max(len(r) for r in rows)
    avg = [""] * width
    avg[label_col] = "Average"
    for col in range(numeric_start, width):
        vals = []
        for row in rows[2:]:
            if row and row[0] == "":
                continue
            if col < len(row):
                val = parse_number(row[col])
                if val is not None:
                    vals.append(val)
        if vals:
            number = mean(vals)
            if all(float(v).is_integer() for v in vals):
                avg[col] = format_int(round(number))
            else:
                avg[col] = format_float(number)
    rows.append([""] * width)
    rows.append(avg)


def generate(args: argparse.Namespace) -> None:
    modules = build_module_records(args.modules_csv, args.original_orders_dir)
    static1 = load_static_table1(args.table1_static)
    static2 = load_static_table2(args.table2_static)
    tuscane_times = load_timing_csv(args.tuscane_timing)
    pairwise = load_pairwise_summary(args.pairwise_summary)
    tuscanic = load_tuscanic_summary(args.tuscanic_summary) if args.tuscanic_summary else {}

    table1_rows: List[List[str]] = [
        ["", "", "Number of", "", "Runtime (in sec.)", "", "Generation time (in sec.)", "", "", ""],
        ["ID", "Module", "Tests", "Test Classes", "Test Suite", "Overhead", "Prior work [10]", "TuscanIC", "Pairwise", "TuscanE"],
    ]

    table2_rows: List[List[str]] = [
        ["", "Number of test orders run", "", "", "", "Number of tests run", "", "", "", "Time to generate and run (in sec.)", "", "", ""],
        ["ID", "Prior work [10]", "TuscanIC", "Pairwise", "TuscanE", "Prior work [10]", "TuscanIC", "Pairwise", "TuscanE", "Prior work [10]", "TuscanIC", "Pairwise", "TuscanE"],
    ]

    for idx, record in enumerate(modules, start=1):
        module = str(record["module"])
        static = static1.get(module, {})
        row_id = static.get("ID", f"M{idx}")

        tuscane_orders, tuscane_tests_run = count_rounds_and_tests(args.tuscane_outputs / module)
        pair_info = pairwise.get(module, {})
        pair_orders = int(pair_info["orders"]) if "orders" in pair_info else None
        pair_tests_run = int(pair_orders * 2) if pair_orders is not None else None
        tuscanic_info = tuscanic.get(module, {})

        table1_rows.append(
            [
                row_id,
                module,
                str(record["tests"]),
                str(record["classes"]),
                static.get("Test Suite", ""),
                static.get("Overhead", ""),
                static.get("Prior work [10]", ""),
                format_float(tuscanic_info.get("duration") if tuscanic_info else None),
                format_float(pair_info.get("duration") if pair_info else None),
                format_float(tuscane_times.get(module)),
            ]
        )

        table2_static = static2.get(row_id, {})
        table2_rows.append(
            [
                row_id,
                table2_static.get("prior_orders", ""),
                format_int(int(tuscanic_info["orders"])) if tuscanic_info else "",
                format_int(pair_orders),
                format_int(tuscane_orders),
                table2_static.get("prior_tests", ""),
                format_int(int(tuscanic_info["tests_run"])) if tuscanic_info else "",
                format_int(pair_tests_run),
                format_int(tuscane_tests_run),
                table2_static.get("prior_time", ""),
                format_float(tuscanic_info.get("duration") if tuscanic_info else None),
                table2_static.get("pairwise_time", ""),
                table2_static.get("tuscane_time", ""),
            ]
        )

    add_average_row(table1_rows, numeric_start=2, label_col=1)
    add_average_row(table2_rows, numeric_start=1, label_col=0)
    write_csv_rows(args.table1_out, table1_rows)
    write_csv_rows(args.table2_out, table2_rows)
    print(f"Wrote {args.table1_out}")
    print(f"Wrote {args.table2_out}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Table 1 and Table 2 CSVs from static paper inputs plus generated order artifacts."
    )
    parser.add_argument("--modules-csv", type=Path, default=REPO_ROOT / "TuscanECodes/modules.csv")
    parser.add_argument("--original-orders-dir", type=Path, default=REPO_ROOT / "TuscanECodes/original-orders")
    parser.add_argument("--tuscane-outputs", type=Path, default=REPO_ROOT / "TuscanECodes/outputs")
    parser.add_argument("--tuscane-timing", type=Path, default=REPO_ROOT / "TuscanECodes/generation_times.csv")
    parser.add_argument("--pairwise-summary", type=Path, default=REPO_ROOT / "pairwise_outputs/summary.csv")
    parser.add_argument("--tuscanic-summary", type=Path, default=None)
    parser.add_argument("--table1-static", type=Path, default=TABLE_DIR / "table-f1.csv")
    parser.add_argument("--table2-static", type=Path, default=TABLE_DIR / "table-f2.csv")
    parser.add_argument("--table1-out", type=Path, default=TABLE_DIR / "generated_table-f1.csv")
    parser.add_argument("--table2-out", type=Path, default=TABLE_DIR / "generated_table-f2.csv")
    return parser.parse_args()


if __name__ == "__main__":
    generate(parse_args())
