#!/usr/bin/env python3
from __future__ import annotations
import csv, re
from pathlib import Path
from typing import List

CSV_PATH = Path("table-f5.csv")
OUT_TEX  = Path("table_f5_def.tex")

MACRO_SUFFIX = "_t5"  # suffix to make all names unique to table 5

def sanitize_col_key(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("/", " per ").replace(" ", "_")
    s = re.sub(r"[^\w]", "_", s, flags=re.UNICODE)
    s = re.sub(r"__+", "_", s).strip("_")
    return s or "Col"

def sanitize_base(s: str) -> str:
    s = (s or "").strip().replace(" ", "-")
    s = re.sub(r"[^A-Za-z0-9\-\.]", "", s)
    return s or "row"

def tex_escape(text: str) -> str:
    repl = [
        ("\\", r"\textbackslash{}"),
        ("{", r"\{"), ("}", r"\}"),
        ("$", r"\$"), ("&", r"\&"), ("#", r"\#"), ("%", r"\%"),
        ("_", r"\_"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]
    out = (text or "")
    for a, b in repl:
        out = out.replace(a, b)
    return out

def read_rows(path: Path) -> List[List[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))

def main() -> None:
    rows = read_rows(CSV_PATH)
    if len(rows) < 3:
        raise ValueError("CSV must include two header rows and at least one data row.")

    header_top, header_bottom = rows[0], rows[1]
    data_rows = rows[2:]
    ncols = max(len(header_top), len(header_bottom), *(len(r) for r in data_rows)) if data_rows else max(len(header_top), len(header_bottom))

    # Build numbered column keys
    col_keys: List[str] = []
    seen: dict[str, int] = {}
    for i in range(ncols):
        raw = (header_bottom[i] if i < len(header_bottom) and header_bottom[i].strip()
               else (header_top[i] if i < len(header_top) else ""))
        base = sanitize_col_key(raw) or "Col"
        seen[base] = seen.get(base, 0) + 1
        col_keys.append(f"{base}_{seen[base]}")  # numbered always

    out = []

    for r in data_rows:
        if all((c or "").strip() == "" for c in r):
            continue
        base = sanitize_base(r[0] if len(r) > 0 else "")
        for ci in range(ncols):
            val = r[ci] if ci < len(r) else ""
            key = f"{base}_{col_keys[ci]}{MACRO_SUFFIX}"
            out.append(f"\\Def{{{key}}}{{{tex_escape(val.strip())}}}")
        out.append("")

    OUT_TEX.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUT_TEX.resolve()}")

if __name__ == "__main__":
    main()