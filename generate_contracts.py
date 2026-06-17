#!/usr/bin/env python3
"""
Generate Insan Biryani employment contracts - v3 (casual, concise, 1-page).
Usage: uv run --with reportlab python generate_contracts.py
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
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

DARK_BROWN  = HexColor('#3D2B1F')
ORANGE      = HexColor('#B8721E')
WARM_BG     = HexColor('#FFF8EE')
WARM_BORDER = HexColor('#D4924A')
SAMPLE_BG   = HexColor('#F5EDD8')
DIVIDER     = HexColor('#CCCCCC')

OUT_DIR = r"C:\Users\fjvat\Projects\insan-biryani-pos\contracts"


def S():
    return {
        'co':  ParagraphStyle('co',  fontName='CalB', fontSize=22, textColor=DARK_BROWN, leading=30, spaceAfter=2),
        'loc': ParagraphStyle('loc', fontName='CalI', fontSize=9,  textColor=HexColor('#666666'), spaceAfter=1),
        'ttl': ParagraphStyle('ttl', fontName='CalB', fontSize=12, textColor=DARK_BROWN, spaceAfter=3),
        'emp': ParagraphStyle('emp', fontName='CalB', fontSize=11, textColor=ORANGE, spaceAfter=1),
        'wl':  ParagraphStyle('wl',  fontName='Cal',  fontSize=9.5, textColor=HexColor('#5C3A1A'), leading=14, alignment=TA_JUSTIFY),
        'sh':  ParagraphStyle('sh',  fontName='CalB', fontSize=9,  textColor=ORANGE, spaceBefore=4, spaceAfter=2),
        'b':   ParagraphStyle('b',   fontName='Cal',  fontSize=8,  leading=12, spaceAfter=1),
        'bj':  ParagraphStyle('bj',  fontName='Cal',  fontSize=8,  leading=12, spaceAfter=1, alignment=TA_JUSTIFY),
        'bl':  ParagraphStyle('bl',  fontName='Cal',  fontSize=8,  leading=12, spaceAfter=2, leftIndent=9),
        'ni':  ParagraphStyle('ni',  fontName='CalI', fontSize=7.5, leading=11, spaceAfter=1, leftIndent=9, textColor=HexColor('#555555')),
        'smb': ParagraphStyle('smb', fontName='CalB', fontSize=8,  leading=12, textColor=DARK_BROWN),
        'smi': ParagraphStyle('smi', fontName='CalI', fontSize=7.5, leading=11, textColor=HexColor('#444444')),
        'sig': ParagraphStyle('sig', fontName='Cal',  fontSize=9,  alignment=TA_CENTER),
        'ft':  ParagraphStyle('ft',  fontName='Cal',  fontSize=8.5, alignment=TA_CENTER, textColor=HexColor('#333333')),
    }


def nb(text, s):
    return Paragraph(f"• {text}", s['bl'])


def col_table(items, col_w):
    t = Table([[item] for item in items], colWidths=[col_w])
    t.setStyle(TableStyle([
        ('TOPPADDING',    (0,0),(-1,-1), 0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 0),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
    ]))
    return t


def generate(filename, employee_name, daily_rate, has_dishwashing):
    os.makedirs(OUT_DIR, exist_ok=True)
    s = S()
    M = 0.40 * inch
    PW, _ = letter
    W = PW - 2 * M

    doc = SimpleDocTemplate(
        os.path.join(OUT_DIR, filename), pagesize=letter,
        leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
    )
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("INSAN BIRYANI", s['co']))
    story.append(Paragraph("Gapan City Plaza Night Market, Nueva Ecija", s['loc']))
    story.append(Paragraph("EMPLOYMENT AGREEMENT", s['ttl']))
    story.append(HRFlowable(width=W, thickness=2, color=ORANGE, spaceAfter=4))
    story.append(Paragraph(f"Para kay: <b>{employee_name}</b>", s['emp']))
    story.append(Spacer(1, 2))

    # ── Welcome box ──────────────────────────────────────────────────────────
    wt = Table([[Paragraph(
        "Welcome sa Insan Biryani! Salamat sa iyong oras at trabaho para sa aming stall. "
        "Basahin nang mabuti ang kasunduang ito at i-sign kapag naiintindihan mo na ang lahat.",
        s['wl'])]], colWidths=[W])
    wt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), WARM_BG),
        ('BOX',           (0,0),(-1,-1), 1.5, WARM_BORDER),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('RIGHTPADDING',  (0,0),(-1,-1), 8),
    ]))
    story.append(wt)
    story.append(Spacer(1, 5))

    # ── Column setup ─────────────────────────────────────────────────────────
    GAP   = 0.10 * inch
    COL_W = (W - GAP) / 2
    SW    = COL_W - 0.08 * inch

    # ════ LEFT COLUMN ════
    left = []

    # 1. Job Description — paragraph form, no bullets
    left.append(Paragraph("1. JOB DESCRIPTION & RESPONSIBILITIES", s['sh']))
    if has_dishwashing:
        left.append(Paragraph(
            "All-around helper ka dito. Tumutulong ka sa lahat — paglilinis, food prep, "
            "pag-serve ng orders, pag-assist sa cashier/POS, at <b>dishwashing</b> ng lahat ng "
            "gamit pagkatapos ng shift.", s['bj']))
    else:
        left.append(Paragraph(
            "All-around helper ka dito. Tumutulong ka sa lahat — paglilinis, food prep, "
            "pag-serve ng orders, at pag-assist sa cashier/POS.", s['bj']))
    left.append(Spacer(1, 3))

    # 2. Work Schedule
    left.append(Paragraph("2. ORAS NG TRABAHO", s['sh']))
    left.append(Paragraph(
        "Shift tuwing gabi: <b>5:00 PM – 10:00 PM</b>. Pumunta ng 5 minuto bago mag-alas singko. "
        "<b>No work, no pay</b> — babayaran ka sa mga gabing talagang pumunta ka.", s['bj']))
    left.append(Spacer(1, 3))

    # 3. Salary
    left.append(Paragraph("3. SAHOD AT DAILY COMMISSION", s['sh']))
    left.append(Paragraph(
        f"Fixed daily pay: <b>₱{daily_rate:,.0f}.00</b> bawat gabing nagtrabaho ka.", s['b']))
    left.append(Spacer(1, 1))
    left.append(Paragraph(
        f"<b>PERO</b> — kung ang benta ng araw ay <b>WALA PANG ₱4,000</b>, "
        f"ang bayad mo ay <b>10% ng total na benta</b>, hindi na ang ₱{daily_rate:,.0f}. "
        f"Para masiguro na may puhunan pa ang stall para bukas.", s['bj']))
    left.append(Spacer(1, 2))

    # Sample box
    st = Table([
        [Paragraph("<b>Halimbawa:</b>", s['smb'])],
        [Paragraph(f"• Benta ₱5,000  →  Kita ₱{daily_rate:,.0f}.00 (fixed)", s['smb'])],
        [Paragraph(f"• Benta ₱4,000  →  Kita ₱{daily_rate:,.0f}.00 (fixed)", s['smb'])],
        [Paragraph(  "• Benta ₱3,500  →  Kita ₱350.00 (10%)", s['smb'])],
        [Paragraph(  "• Benta ₱2,800  →  Kita ₱280.00 (10%)", s['smb'])],
    ], colWidths=[SW])
    st.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), SAMPLE_BG),
        ('BOX',           (0,0),(-1,-1), 1, DARK_BROWN),
        ('TOPPADDING',    (0,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,0),(-1,-1), 3),
        ('LEFTPADDING',   (0,0),(-1,-1), 5),
        ('RIGHTPADDING',  (0,0),(-1,-1), 5),
    ]))
    left.append(st)
    left.append(Spacer(1, 1))
    monthly = daily_rate * 26
    left.append(Paragraph(
        f"<i>Monthly estimate: ₱{daily_rate:,.0f} × 26 araw = ₱{monthly:,.0f}/buwan</i>", s['ni']))
    left.append(Spacer(1, 3))

    # 4. House Rules
    left.append(Paragraph("4. HOUSE RULES", s['sh']))
    for rule in [
        "Panatilihing malinis ang lugar. Huwag mag-aksaya ng pagkain.",
        "Laging mag-gloves kapag nag-aayos ng orders. Mag-offer sa mga customers.",
        "I-record nang tama ang lahat ng bayad. Huwag kumuha ng pera o pagkain nang walang pahintulot.",
        "Malinis na damit, nakaayos na buhok, at regular na paghuhugas ng kamay.",
        "Kung hindi makapasok, abisuhan ang may-ari ng 4 oras bago ang 5 PM.",
        "Laging ngumiti at maging magalang. Bawal ang away at gulo.",
    ]:
        left.append(nb(rule, s))

    # ════ RIGHT COLUMN ════
    right = []

    # 5. Benefits
    right.append(Paragraph("5. MGA BENEPISYO", s['sh']))
    right.append(nb(
        "<b>Daily Cash:</b> Ibinibigay ang bayad mo sa katapusan ng bawat shift — cash, araw-araw.", s))
    right.append(nb(
        "<b>Sales Bonus:</b> Kung mataas ang benta lalo na sa <b>ber months (Sep–Dec)</b>, "
        "may bonus. Depende sa actual na sales at desisyon ng may-ari.", s))
    right.append(Spacer(1, 3))

    # 6. Policies
    right.append(Paragraph("6. POLICIES & PROCEDURES", s['sh']))
    right.append(nb(
        "<b>Honesty:</b> I-record nang tama ang lahat ng transaksyon. "
        "Huwag kumuha ng pera o pagkain nang walang pahintulot.", s))
    right.append(nb(
        "<b>Kalinisan:</b> Malinis na damit at nakaayos na buhok. "
        "Maghugas ng kamay gamit ang sabon.", s))
    right.append(nb(
        "<b>Absences:</b> Abisuhan ang may-ari ng hindi bababa sa 4 na oras "
        "bago ang 5 PM kung hindi ka makapasok.", s))
    right.append(Spacer(1, 3))

    # 7. Training
    right.append(Paragraph("7. TRAINING PERIOD", s['sh']))
    right.append(Paragraph(
        "<b>1 araw ang training, walang bayad.</b> Magsisimula agad sa unang hapon mo "
        "at magtratrabaho ka na sa stall pagdating ng gabi.", s['bj']))
    right.append(Spacer(1, 3))

    # 8. Confidentiality
    right.append(Paragraph("8. CONFIDENTIALITY", s['sh']))
    right.append(Paragraph(
        "Huwag ibabahagi ang aming recipes, paraan ng pagluluto, at daily sales "
        "sa kahit sino sa labas ng Insan Biryani.", s['bj']))
    right.append(Spacer(1, 3))

    # 9. Termination
    right.append(Paragraph("9. PAG-ALIS SA TRABAHO", s['sh']))
    right.append(Paragraph(
        "Mag-bigay ng <b>3-araw na abiso</b> bago mag-resign. Kung may malaking paglabag — "
        "tulad ng pagnanakaw o paulit-ulit na absent nang walang dahilan — "
        "maaaring tanggalin agad.", s['bj']))

    # ── Two-column table ──────────────────────────────────────────────────
    two_col = Table(
        [[col_table(left, COL_W), col_table(right, COL_W)]],
        colWidths=[COL_W, COL_W], hAlign='LEFT',
    )
    two_col.setStyle(TableStyle([
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 0),
        ('LINEAFTER',     (0,0),(0,-1),  0.5, DIVIDER),
        ('RIGHTPADDING',  (0,0),(0,-1),  7),
        ('LEFTPADDING',   (1,0),(1,-1),  7),
    ]))
    story.append(two_col)

    # ── Signature (kept together, always 1 page) ─────────────────────────
    HW = W / 2
    sig_tbl = Table([
        [Paragraph(" ", s['sig']), Paragraph(" ", s['sig'])],
        [Paragraph(f"Helper: {employee_name}", s['sig']),
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
    story.append(KeepTogether([
        Spacer(1, 6),
        HRFlowable(width=W, thickness=1, color=DIVIDER, spaceAfter=3),
        Paragraph(
            "Sa pag-sign sa ibaba, naintindihan mo at sang-ayon ka sa lahat ng nakasulat dito.",
            s['ft']),
        Spacer(1, 14),
        sig_tbl,
    ]))

    doc.build(story)
    print(f"  OK  {filename}")


if __name__ == '__main__':
    print("Generating Insan Biryani contracts (v3)...\n")
    for name in ["Krystal Jhem Robles", "Melody De Guzman", "Yassy Centeno"]:
        generate("contract_" + name.lower().replace(' ', '_') + ".pdf", name, 400, False)
    generate("contract_krissa_ramos.pdf", "Krissa Ramos", 500, True)
    print(f"\nDone! Saved to: {OUT_DIR}")
