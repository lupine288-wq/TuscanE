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


def read_csv(path: Path) -> List[List[str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def write_csv(path: Path, rows: Iterable[Iterable[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def parse_num(value: str | None) -> Optional[float]:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt_int(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{round(value):,}"


def fmt_float(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def module_name(project: str, module: str) -> str:
    return project.split("/")[-1] if module == "." else Path(module).name


def original_order_name(project: str, sha: str, module: str) -> str:
    return f"{project.replace('/', '_')}-{module.replace('/', '_')}-{sha[:7]}-original_order"


def class_name(test_name: str) -> str:
    if "#" in test_name:
        return test_name.rsplit("#", 1)[0]
    if "." in test_name:
        return test_name.rsplit(".", 1)[0]
    return test_name


def read_tests(path: Path) -> List[str]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


def load_modules(modules_csv: Path, original_orders_dir: Path) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for row in read_csv(modules_csv):
        if len(row) < 3 or row[0] == "Project":
            continue
        project, sha, module = row[:3]
        short_module = module_name(project, module)
        tests = read_tests(original_orders_dir / original_order_name(project, sha, module))
        records.append(
            {
                "project": project,
                "sha": sha,
                "module_path": module,
                "module": short_module,
                "tests": len(tests),
                "classes": len({class_name(t) for t in tests}),
            }
        )
    return records


def load_static_table1(path: Path) -> Dict[str, Dict[str, str]]:
    rows = read_csv(path)
    if len(rows) < 2:
        return {}
    header = rows[1]
    result: Dict[str, Dict[str, str]] = {}
    for row in rows[2:]:
        if not row or not row[0].strip() or len(row) < 2:
            continue
        values = {header[i]: row[i] if i < len(row) else "" for i in range(len(header))}
        result[values["Module"]] = values
    return result


def load_static_table2(path: Path) -> Dict[str, Dict[str, str]]:
    rows = read_csv(path)
    result: Dict[str, Dict[str, str]] = {}
    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        result[row[0]] = {
            "tuscane_time": row[9] if len(row) > 9 else "",
            "pairwise_time": row[8] if len(row) > 8 else "",
        }
    return result


def load_timing(path: Path) -> Dict[str, float]:
    result: Dict[str, float] = {}
    for row in read_csv(path):
        if len(row) < 5:
            continue
        seconds = parse_num(row[-1])
        if seconds is None:
            continue
        result[module_name(row[0], row[2])] = seconds
    return result


def load_pairwise_summary(path: Path) -> Dict[str, Dict[str, Optional[float]]]:
    result: Dict[str, Dict[str, Optional[float]]] = {}
    if not path.is_file():
        return result
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out_dir = row.get("output_subfolder", "")
            module = Path(out_dir).name if out_dir else Path(row.get("input_file", "")).stem
            result[module] = {
                "orders": parse_num(row.get("num_orders")),
                "tests": parse_num(row.get("num_tests")),
                "duration": parse_num(row.get("duration_seconds")),
            }
    return result


def load_tuscanic_summary(path: Optional[Path]) -> Dict[str, Dict[str, Optional[float]]]:
    if not path or not path.is_file():
        return {}
    result: Dict[str, Dict[str, Optional[float]]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            module = row.get("module") or row.get("Module") or row.get("output_subfolder") or ""
            module = Path(module).name
            if not module:
                continue
            result[module] = {
                "orders": parse_num(row.get("num_orders")),
                "tests_run": parse_num(row.get("num_tests_run")),
                "duration": parse_num(row.get("duration_seconds")),
            }
    return result


def load_random_projectlist(path: Path) -> Dict[str, float]:
    result: Dict[str, float] = {}
    if not path.is_file():
        return result
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            module = row.get("Module", "")
            count = parse_num(row.get("maxordercount"))
            if module and count is not None:
                result[Path(module).name] = count
    return result


def count_json_orders(module_dir: Path) -> Tuple[Optional[int], Optional[int]]:
    if not module_dir.is_dir():
        return None, None
    orders = 0
    tests_run = 0
    for path in module_dir.glob("round*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        order = data.get("testOrder", [])
        if isinstance(order, list):
            orders += 1
            tests_run += len(order)
    return orders, tests_run


def add_average(rows: List[List[str]], first_numeric_col: int, label_col: int) -> None:
    width = max(len(r) for r in rows)
    avg = [""] * width
    avg[label_col] = "Average"
    for col in range(first_numeric_col, width):
        values = []
        for row in rows[2:]:
            if row and row[0] == "":
                continue
            if col < len(row):
                value = parse_num(row[col])
                if value is not None:
                    values.append(value)
        if values:
            value = mean(values)
            avg[col] = fmt_int(value) if all(v.is_integer() for v in values) else fmt_float(value)
    rows.append([""] * width)
    rows.append(avg)


def build_tables(args: argparse.Namespace) -> None:
    modules = load_modules(args.modules_csv, args.original_orders_dir)
    table1_static = load_static_table1(args.table1_static)
    table2_static = load_static_table2(args.table2_static)
    tuscane_timing = load_timing(args.tuscane_timing)
    pairwise = load_pairwise_summary(args.pairwise_summary)
    tuscanic = load_tuscanic_summary(args.tuscanic_summary)
    random_orders = load_random_projectlist(args.projectlist)

    table1 = [
        ["", "", "Number of", "", "Runtime (in sec.)", "", "Generation time (in sec.)", "", ""],
        ["ID", "Module", "Tests", "Test Classes", "Test Suite", "Overhead", "TuscanIC", "Pairwise", "TuscanE"],
    ]
    table2 = [
        ["", "Number of test orders run", "", "", "Number of tests run", "", "", "Time to generate and run (in sec.)", "", ""],
        ["ID", "TuscanIC", "Pairwise", "TuscanE", "TuscanIC", "Pairwise", "TuscanE", "TuscanIC", "Pairwise", "TuscanE"],
    ]
    table3 = [
        [
            "ID",
            "Generation time (in sec.)", "", "", "", "", "",
            "Number of test orders run", "", "", "", "", "",
            "Number of tests run", "", "", "", "", "",
            "Time to generate and run (in sec.)", "", "", "", "", "",
        ],
        [
            "",
            "Red. tests", "Full Testsuite", "Random", "TuscanIC", "Pairwise", "TuscanE",
            "Red. tests", "Full Testsuite", "Random", "TuscanIC", "Pairwise", "TuscanE",
            "Red. tests", "Full Testsuite", "Random", "TuscanIC", "Pairwise", "TuscanE",
            "Red. tests", "Full Testsuite", "Random", "TuscanIC", "Pairwise", "TuscanE",
        ],
    ]

    for idx, record in enumerate(modules, start=1):
        module = str(record["module"])
        static1 = table1_static.get(module, {})
        row_id = static1.get("ID", f"M{idx}")
        static2 = table2_static.get(row_id, {})
        pair = pairwise.get(module, {})
        ic = tuscanic.get(module, {})
        tuscane_orders, tuscane_tests = count_json_orders(args.tuscane_outputs / module)

        pair_orders = pair.get("orders")
        pair_tests_run = pair_orders * 2 if pair_orders is not None else None
        random_count = random_orders.get(module)
        random_tests_run = random_count * int(record["tests"]) if random_count is not None else None

        table1.append([
            row_id,
            module,
            str(record["tests"]),
            str(record["classes"]),
            static1.get("Test Suite", ""),
            static1.get("Overhead", ""),
            fmt_float(ic.get("duration")) if ic else "",
            fmt_float(pair.get("duration")) or static1.get("Pairwise", ""),
            fmt_float(tuscane_timing.get(module)),
        ])

        table2.append([
            row_id,
            fmt_int(ic.get("orders")) if ic else "",
            fmt_int(pair_orders),
            fmt_int(tuscane_orders),
            fmt_int(ic.get("tests_run")) if ic else "",
            fmt_int(pair_tests_run),
            fmt_int(tuscane_tests),
            fmt_float(ic.get("duration")) if ic else "",
            static2.get("pairwise_time", ""),
            static2.get("tuscane_time", ""),
        ])

        table3.append([
            row_id,
            "", "", "", fmt_float(ic.get("duration")) if ic else "", fmt_float(pair.get("duration")) or static1.get("Pairwise", ""), fmt_float(tuscane_timing.get(module)),
            "", "", fmt_int(random_count), fmt_int(ic.get("orders")) if ic else "", fmt_int(pair_orders), fmt_int(tuscane_orders),
            "", "", fmt_int(random_tests_run), fmt_int(ic.get("tests_run")) if ic else "", fmt_int(pair_tests_run), fmt_int(tuscane_tests),
            "", "", "", fmt_float(ic.get("duration")) if ic else "", static2.get("pairwise_time", ""), static2.get("tuscane_time", ""),
        ])

    add_average(table1, first_numeric_col=2, label_col=1)
    add_average(table2, first_numeric_col=1, label_col=0)
    add_average(table3, first_numeric_col=1, label_col=0)

    write_csv(args.table1_out, table1)
    write_csv(args.table2_out, table2)
    write_csv(args.table3_out, table3)
    print(f"Wrote {args.table1_out}")
    print(f"Wrote {args.table2_out}")
    print(f"Wrote {args.table3_out}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper Table 1, Table 2, and Table 3 CSVs from available artifacts.")
    parser.add_argument("--modules-csv", type=Path, default=REPO_ROOT / "TuscanECodes/modules.csv")
    parser.add_argument("--original-orders-dir", type=Path, default=REPO_ROOT / "TuscanECodes/original-orders")
    parser.add_argument("--tuscane-outputs", type=Path, default=REPO_ROOT / "TuscanECodes/outputs")
    parser.add_argument("--tuscane-timing", type=Path, default=REPO_ROOT / "TuscanECodes/generation_times.csv")
    parser.add_argument("--pairwise-summary", type=Path, default=REPO_ROOT / "pairwise_outputs/summary.csv")
    parser.add_argument("--projectlist", type=Path, default=REPO_ROOT / "projectlist.csv")
    parser.add_argument("--tuscanic-summary", type=Path, default=None)
    parser.add_argument("--table1-static", type=Path, default=TABLE_DIR / "table-f1.csv")
    parser.add_argument("--table2-static", type=Path, default=TABLE_DIR / "table-f2.csv")
    parser.add_argument("--table1-out", type=Path, default=TABLE_DIR / "generated_table-f1.csv")
    parser.add_argument("--table2-out", type=Path, default=TABLE_DIR / "generated_table-f2.csv")
    parser.add_argument("--table3-out", type=Path, default=TABLE_DIR / "generated_table-f3.csv")
    return parser.parse_args()


if __name__ == "__main__":
    build_tables(parse_args())
