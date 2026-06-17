#!/usr/bin/env python3
"""
Generate Insan Biryani employment contracts - v4 (plain, one-page, paragraph-based English).
Usage (from repo root): uv run --with reportlab --with pillow python contracts/generate_contracts.py
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
    Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Calibri TTF for ₱ peso sign ─────────────────────────────────────────────
F = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Cal',   f'{F}/calibri.ttf'))
pdfmetrics.registerFont(TTFont('CalB',  f'{F}/calibrib.ttf'))
pdfmetrics.registerFont(TTFont('CalI',  f'{F}/calibrii.ttf'))
pdfmetrics.registerFont(TTFont('CalBI', f'{F}/calibriz.ttf'))
pdfmetrics.registerFontFamily('Cal', normal='Cal', bold='CalB', italic='CalI', boldItalic='CalBI')

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(OUT_DIR, "logo.jpg")
LOGO_ASPECT = 1592 / 1536  # native logo.jpg pixel size
COMMISSION_RATE = 0.10
DISHWASHING_BONUS = 100

# ── Brand palette, sampled from logo.jpg ────────────────────────────────────
RUST_HEX   = '#BA4B16'
RUST       = HexColor(RUST_HEX)
DARK_BROWN = HexColor('#2C1F0E')
CREAM      = HexColor('#F4E4C3')

NAME_BLANK = "_______________"


def rb(text):
    """Bold text in the brand rust color, for money/percentage/time figures."""
    return f'<font color="{RUST_HEX}"><b>{text}</b></font>'


def S():
    return {
        'co':  ParagraphStyle('co',  fontName='CalB', fontSize=16, leading=20, textColor=DARK_BROWN, spaceAfter=2),
        'loc': ParagraphStyle('loc', fontName='CalI', fontSize=9,  textColor=DARK_BROWN, spaceAfter=4),
        'ttl': ParagraphStyle('ttl', fontName='CalB', fontSize=12, textColor=RUST, spaceAfter=0),
        'p':   ParagraphStyle('p',   fontName='Cal',  fontSize=10.5, leading=15, textColor=DARK_BROWN, alignment=TA_JUSTIFY, spaceAfter=10),
        'bl':  ParagraphStyle('bl',  fontName='Cal',  fontSize=10.5, leading=15, textColor=DARK_BROWN, leftIndent=18, spaceAfter=3),
        'sig': ParagraphStyle('sig', fontName='Cal',  fontSize=10, textColor=DARK_BROWN, alignment=TA_CENTER),
        'box': ParagraphStyle('box', fontName='Cal',  fontSize=10.5, leading=15, textColor=DARK_BROWN, alignment=TA_JUSTIFY, spaceAfter=6),
    }


def generate(filename, employee_name, daily_rate):
    os.makedirs(OUT_DIR, exist_ok=True)
    s = S()
    M = 1 * inch
    PW, _ = letter
    W = PW - 2 * M
    name_field = employee_name if employee_name else NAME_BLANK

    doc = SimpleDocTemplate(
        os.path.join(OUT_DIR, filename), pagesize=letter,
        leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
    )
    story = []

    # ── Header: logo + name/title letterhead ───────────────────────────────
    logo_h = 0.95 * inch
    logo_w = logo_h * LOGO_ASPECT
    header_text = [
        Paragraph("INSAN BIRYANI", s['co']),
        Paragraph("Gapan City Plaza Night Market, Nueva Ecija", s['loc']),
        Paragraph("Payment Agreement Contract", s['ttl']),
    ]
    header_tbl = Table(
        [[Image(LOGO_PATH, width=logo_w, height=logo_h), header_text]],
        colWidths=[logo_w + 0.15 * inch, W - logo_w - 0.15 * inch],
    )
    header_tbl.setStyle(TableStyle([
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 0),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width=W, thickness=1.5, color=RUST, spaceAfter=12))

    # ── Intro ───────────────────────────────────────────────────────────────
    story.append(Paragraph(
        f"This agreement is between <b>Insan Biryani</b> (\"the Stall\") and "
        f"<b>{name_field}</b> (\"the Helper\"), for work at the food stall in "
        f"Gapan City Plaza Night Market, Nueva Ecija.", s['p']))

    # ── Duties ──────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "The Helper agrees to work as an all-around helper at the stall, "
        "assisting with food preparation, serving orders, helping at the "
        "cashier / POS, and keeping the stall clean.", s['p']))

    # ── Schedule ────────────────────────────────────────────────────────────
    story.append(Paragraph(
        f"The Helper's shift is every night from {rb('5:00 PM to 10:00 PM')}, "
        f"and the Helper should arrive 5 minutes early. Pay is given only for "
        f"nights actually worked — no work, no pay.", s['p']))

    # ── Salary ──────────────────────────────────────────────────────────────
    threshold = daily_rate / COMMISSION_RATE
    commission_phrase = rb("10% of that day's total sales")
    salary_text = (
        f"The Helper will be paid a fixed amount of {rb(f'₱{daily_rate:,.0f}.00')} "
        f"for every night worked, paid in cash at the end of each shift. "
        f"However, if the stall's total sales for that day are below "
        f"{rb(f'₱{threshold:,.0f}')}, the Helper will instead be paid "
        f"{commission_phrase}, so the stall still has "
        f"enough money to restock for the next day.")
    story.append(Paragraph(salary_text, s['p']))

    story.append(Paragraph("This works out as follows:", s['p']))
    for sales, fixed in [(5000, True), (4000, True), (3500, False), (2800, False)]:
        total = daily_rate if fixed else sales * COMMISSION_RATE
        basis = "fixed" if fixed else "10%"
        story.append(Paragraph(
            f"•  Sales ₱{sales:,.0f} → Pay ₱{total:,.0f}.00 ({basis})", s['bl']))
    story.append(Spacer(1, 6))

    highlight_box = Table([[[
        Paragraph(
            f"<b>Note:</b> If the Helper also washes the dishes herself after "
            f"each shift, she will receive an additional "
            f"{rb(f'₱{DISHWASHING_BONUS:,.0f}.00')} for that night, on top of "
            f"the amount above.", s['box']),
        Paragraph(
            f"On nights when sales are especially high — especially during "
            f"the {rb('ber months (September to December)')} — the Helper "
            f"may also receive a bonus, depending on actual sales and at the "
            f"Stall Owner's discretion.", s['box']),
    ]]], colWidths=[W])
    highlight_box.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), CREAM),
        ('BOX',           (0,0),(-1,-1), 1.2, RUST),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
        ('RIGHTPADDING',  (0,0),(-1,-1), 10),
    ]))
    story.append(highlight_box)
    story.append(Spacer(1, 10))

    # ── Closing ─────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "By signing below, both parties agree to the terms described above. "
        "Both parties will receive a copy of this agreement.", s['p']))

    # ── Signature ───────────────────────────────────────────────────────────
    HW = W / 2
    sig_tbl = Table([
        [Paragraph(" ", s['sig']), Paragraph(" ", s['sig'])],
        [Paragraph(f"Helper: {name_field}", s['sig']),
         Paragraph("Stall Owner / Insan Biryani", s['sig'])],
        [Paragraph("Date Signed: _______________", s['sig']),
         Paragraph("Date Signed: _______________", s['sig'])],
    ], colWidths=[HW, HW], rowHeights=[22, None, None])
    sig_tbl.setStyle(TableStyle([
        ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
        ('VALIGN',        (0,0),(-1,-1), 'BOTTOM'),
        ('TOPPADDING',    (0,0),(-1,-1), 2),
        ('BOTTOMPADDING', (0,0),(-1,-1), 2),
        ('LINEBELOW',     (0,0),(1, 0),  1, black),
    ]))
    story.append(KeepTogether([Spacer(1, 18), sig_tbl]))

    doc.build(story)
    print(f"  OK  {filename}")


if __name__ == '__main__':
    print("Generating Insan Biryani contracts (v4)...\n")
    for name in ["Krystal Jhem Robles", "Melody De Guzman", "Yassy Centeno", "Krissa Ramos"]:
        generate("contract_" + name.lower().replace(' ', '_') + ".pdf", name, 400)
    generate("contract_template.pdf", None, 400)
    print(f"\nDone! Saved to: {OUT_DIR}")
