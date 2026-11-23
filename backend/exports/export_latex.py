from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Any


def escape_latex(value: Any) -> str:
    s = str(value)
    return (s.replace("\\", "\\textbackslash{}")
             .replace("_", "\\_")
             .replace("%", "\\%")
             .replace("&", "\\&")
             .replace("#", "\\#"))


def write_latex_table(path: str | Path, rows: List[Dict[str, Any]], caption: str, label: str, max_rows: int = 20) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        p.write_text("% No rows available\n", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    colspec = "l" * len(fields)
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        f"\\caption{{{escape_latex(caption)}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{colspec}}}",
        "\\hline",
    ]
    lines.append(" & ".join(escape_latex(f) for f in fields) + r" \\")
    lines.append("\\hline")
    for row in rows[:max_rows]:
        lines.append(" & ".join(escape_latex(row.get(f, "")) for f in fields) + r" \\")
    lines += ["\\hline", "\\end{tabular}", "\\end{table*}"]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
