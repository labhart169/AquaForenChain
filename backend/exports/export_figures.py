from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any


def write_simple_svg_bar(path: str | Path, rows: List[Dict[str, Any]], x_key: str, y_key: str, title: str) -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 520
    margin = 70
    vals = [float(r[y_key]) for r in rows if str(r.get(y_key, "")).replace('.', '', 1).isdigit()]
    maxv = max(vals) if vals else 1.0
    bar_w = max(12, int((width - 2 * margin) / max(1, len(rows))) - 8)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="white"/>']
    svg.append(f'<text x="{width/2}" y="35" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>')
    svg.append(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="black"/>')
    svg.append(f'<line x1="{margin}" y1="{height-margin}" x2="{margin}" y2="{margin}" stroke="black"/>')
    for i, r in enumerate(rows):
        val = float(r.get(y_key, 0) or 0)
        x = margin + i * ((width - 2*margin) / max(1, len(rows))) + 4
        h = (val / maxv) * (height - 2*margin - 40)
        y = height - margin - h
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="#cccccc" stroke="black"/>')
        svg.append(f'<text x="{x+bar_w/2:.1f}" y="{height-margin+18}" text-anchor="middle" font-size="11" font-family="Arial">{r.get(x_key, i)}</text>')
    svg.append('</svg>')
    p.write_text("\n".join(svg), encoding="utf-8")
