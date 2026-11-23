from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Any


def write_excel(path: str | Path, sheets: Dict[str, List[Dict[str, Any]]]) -> str:
    """Write xlsx if openpyxl is available, otherwise write CSV fallbacks."""
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    try:
        from openpyxl import Workbook
    except Exception:
        from .export_csv import write_csv
        for name, rows in sheets.items():
            write_csv(p.with_name(f"{p.stem}_{name}.csv"), rows)
        return "CSV_FALLBACK_OPENPYXL_NOT_INSTALLED"
    wb = Workbook()
    first = True
    for name, rows in sheets.items():
        ws = wb.active if first else wb.create_sheet()
        first = False
        ws.title = name[:31]
        if rows:
            fields = sorted({k for row in rows for k in row.keys()})
            ws.append(fields)
            for row in rows:
                ws.append([row.get(k, "") for k in fields])
    wb.save(p)
    return "XLSX_WRITTEN"
