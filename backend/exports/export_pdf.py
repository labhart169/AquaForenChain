from __future__ import annotations
from pathlib import Path


def write_report(path: str | Path, title: str, lines: list[str]) -> str:
    """Write a PDF if reportlab exists; otherwise write a Markdown fallback."""
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        md = p.with_suffix('.md')
        md.write_text('# ' + title + '\n\n' + '\n'.join(f'- {x}' for x in lines) + '\n', encoding='utf-8')
        return "MARKDOWN_FALLBACK_REPORTLAB_NOT_INSTALLED"
    c = canvas.Canvas(str(p), pagesize=A4)
    width, height = A4
    y = height - 60
    c.setFont("Helvetica-Bold", 15); c.drawString(50, y, title); y -= 35
    c.setFont("Helvetica", 10)
    for line in lines:
        c.drawString(50, y, line[:105]); y -= 16
        if y < 50:
            c.showPage(); y = height - 50; c.setFont("Helvetica", 10)
    c.save()
    return "PDF_WRITTEN"
