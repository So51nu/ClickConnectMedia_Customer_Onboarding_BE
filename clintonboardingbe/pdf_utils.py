# # pdf_utils.py
# import io
# from datetime import datetime

# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_LEFT, TA_CENTER
# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     Table,
#     TableStyle,
#     PageBreak,
#     Image,
# )
# from reportlab.pdfgen import canvas as canvas_module


# # ------------------------------------------------------------
# # CONFIG
# # ------------------------------------------------------------
# COMPANY_NAME = "Click Connect Media Pvt. Ltd."
# COMPANY_TAGLINE = "Digital Marketing & Communication Services"

# COMPANY_ADDR_LINES = [
#     "Office No 301, B Wing, Kemp Plaza, Malad, Mindspace, Malad West",
#     "Mumbai, Maharashtra 400064",
#     "info@clickconnectmedia.in | www.clickconnectmedia.in",
#     "+91 9892631244",
# ]

# WATERMARK_TEXT = "Click Connect Media Pvt Ltd"

# # More subtle watermark
# WATERMARK_COLOR = colors.Color(0.10, 0.35, 0.75, alpha=0.08)


# # ------------------------------------------------------------
# # Helpers
# # ------------------------------------------------------------
# def _exists_filefield(ff):
#     try:
#         return bool(ff) and bool(getattr(ff, "path", None))
#     except Exception:
#         return False


# def _safe_image_flowable(file_field, width: float, height: float):
#     try:
#         if not _exists_filefield(file_field):
#             return None
#         return Image(file_field.path, width=width, height=height)
#     except Exception:
#         return None


# def _wrap_text_to_width(c, text: str, max_width: float, font_name: str, font_size: int):
#     """
#     Wraps text into multiple lines so that each line fits max_width.
#     """
#     if not text:
#         return [""]

#     c.saveState()
#     c.setFont(font_name, font_size)

#     words = text.split()
#     lines = []
#     cur = ""

#     for w in words:
#         test = (cur + " " + w).strip()
#         if c.stringWidth(test, font_name, font_size) <= max_width:
#             cur = test
#         else:
#             if cur:
#                 lines.append(cur)
#             cur = w

#     if cur:
#         lines.append(cur)

#     c.restoreState()
#     return lines


# def build_application_pdf(app, company_signature_path=None):
#     """
#     FIXED:
#     ✅ duplicate pages removed (no custom canvas replay)
#     ✅ header alignment fixed (right block wrapped + smaller font)
#     ✅ watermark clipped to content area (no ugly overlay on header/footer)
#     ✅ better spacing
#     """
#     buf = io.BytesIO()

#     # Layout constants
#     page_w, page_h = A4
#     HEADER_H = 3.0 * cm
#     FOOTER_H = 1.7 * cm

#     doc = SimpleDocTemplate(
#         buf,
#         pagesize=A4,
#         leftMargin=1.6 * cm,
#         rightMargin=1.6 * cm,
#         topMargin=(HEADER_H + 1.7 * cm),   # space for header + spacing
#         bottomMargin=(FOOTER_H + 0.7 * cm) # footer space
#     )

#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(name="SecTitle", fontSize=12.5, leading=16, spaceAfter=8, alignment=TA_LEFT))
#     styles.add(ParagraphStyle(name="Small", fontSize=9.2, leading=11.5, alignment=TA_LEFT))
#     styles.add(ParagraphStyle(name="SmallC", fontSize=9.2, leading=11.5, alignment=TA_CENTER))

#     def p(txt, style="Small"):
#         return Paragraph(txt, styles[style])

#     def yesno(v):
#         return "Yes" if bool(v) else "No"

#     def services_list():
#         try:
#             s = app.services_list()
#             return s if s else []
#         except Exception:
#             csv = getattr(app, "services_csv", "") or ""
#             return [x.strip() for x in csv.split(",") if x.strip()]

#     def two_col_table(rows, col_widths=(6.0 * cm, 10.0 * cm)):
#         data = []
#         for k, v in rows:
#             val = v if v not in (None, "") else "-"
#             data.append([p(f"<b>{k}</b>"), p(str(val))])

#         t = Table(data, colWidths=list(col_widths), hAlign="LEFT")
#         t.setStyle(TableStyle([
#             ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
#             ("BOX", (0, 0), (-1, -1), 0.9, colors.lightgrey),
#             ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
#             ("VALIGN", (0, 0), (-1, -1), "TOP"),
#             ("LEFTPADDING", (0, 0), (-1, -1), 8),
#             ("RIGHTPADDING", (0, 0), (-1, -1), 8),
#             ("TOPPADDING", (0, 0), (-1, -1), 6),
#             ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
#         ]))
#         return t

#     def img_cell(file_field, w=7.8 * cm, h=4.6 * cm):
#         img = _safe_image_flowable(file_field, width=w, height=h)
#         if img:
#             return img
#         return p("<i>- Not provided -</i>", "SmallC")

#     generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # ------------------------------------------------------------
#     # Header + Footer + Watermark
#     # ------------------------------------------------------------
#     def _draw_header(c: canvas_module.Canvas):
#         # Background bar
#         c.saveState()
#         c.setFillColor(colors.HexColor("#2B4056"))
#         c.rect(0, page_h - HEADER_H, page_w, HEADER_H, fill=1, stroke=0)

#         # Left icon (simple)
#         icon_x = 1.0 * cm
#         icon_y = page_h - 2.1 * cm
#         c.setStrokeColor(colors.HexColor("#3FA9F5"))
#         c.setLineWidth(3)
#         c.line(icon_x + 0.3 * cm, icon_y - 0.2 * cm, icon_x + 0.3 * cm, icon_y + 0.8 * cm)
#         c.arc(icon_x - 0.1 * cm, icon_y + 0.1 * cm, icon_x + 0.7 * cm, icon_y + 0.9 * cm, 30, 150)
#         c.arc(icon_x - 0.4 * cm, icon_y + 0.0 * cm, icon_x + 1.0 * cm, icon_y + 1.1 * cm, 30, 150)

#         # Left title area
#         left_text_x = 2.0 * cm
#         c.setFillColor(colors.white)
#         c.setFont("Helvetica-Bold", 21)
#         c.drawString(left_text_x, page_h - 1.35 * cm, COMPANY_NAME)
#         c.setFont("Helvetica", 11)
#         c.drawString(left_text_x, page_h - 2.15 * cm, COMPANY_TAGLINE)

#         # Right address area (WRAPPED + smaller font)
#         right_margin = 1.1 * cm
#         right_x = page_w - right_margin

#         # We must avoid overlap: reserve a "right block width"
#         right_block_width = 7.4 * cm  # fixed width so it won't collide with left title
#         right_block_left_x = right_x - right_block_width

#         c.setFont("Helvetica", 9)
#         y = page_h - 1.15 * cm

#         for raw_line in COMPANY_ADDR_LINES:
#             lines = _wrap_text_to_width(c, raw_line, right_block_width, "Helvetica", 9)
#             for ln in lines:
#                 c.drawRightString(right_x, y, ln)
#                 y -= 0.5 * cm

#         c.restoreState()

#         # divider
#         c.saveState()
#         c.setStrokeColor(colors.lightgrey)
#         c.setLineWidth(1)
#         c.line(1.2 * cm, page_h - HEADER_H - 0.1 * cm, page_w - 1.2 * cm, page_h - HEADER_H - 0.1 * cm)
#         c.restoreState()

#     def _draw_footer(c: canvas_module.Canvas):
#         c.saveState()
#         c.setStrokeColor(colors.lightgrey)
#         c.setLineWidth(1)
#         c.line(1.2 * cm, 1.7 * cm, page_w - 1.2 * cm, 1.7 * cm)

#         c.setFont("Helvetica", 8.8)
#         c.setFillColor(colors.grey)
#         c.drawString(1.2 * cm, 1.1 * cm, COMPANY_NAME)
#         c.drawCentredString(page_w / 2, 1.1 * cm, f"Generated: {generated_at}")
#         c.drawRightString(page_w - 1.2 * cm, 1.1 * cm, f"Page {c.getPageNumber()}")
#         c.restoreState()

#     def _draw_watermark_full_area(c: canvas_module.Canvas):
#         """
#         Full page watermark BUT clip into content area (exclude header/footer)
#         so it looks clean and readable.
#         """
#         c.saveState()

#         # Clip region: below header divider and above footer divider
#         clip_x = 0
#         clip_y = FOOTER_H
#         clip_w = page_w
#         clip_h = page_h - HEADER_H - FOOTER_H

#         path = c.beginPath()
#         path.rect(clip_x, clip_y, clip_w, clip_h)
#         c.clipPath(path, stroke=0, fill=0)

#         c.setFillColor(WATERMARK_COLOR)
#         c.setFont("Helvetica-Bold", 26)

#         # Tile settings (less clutter than before)
#         step_x = 9.0 * cm
#         step_y = 5.0 * cm

#         c.translate(page_w / 2, page_h / 2)
#         c.rotate(35)

#         start_x = -page_w
#         end_x = page_w
#         start_y = -page_h
#         end_y = page_h

#         y = start_y
#         while y <= end_y:
#             x = start_x
#             while x <= end_x:
#                 c.drawString(x, y, WATERMARK_TEXT)
#                 x += step_x
#             y += step_y

#         c.restoreState()

#     def _on_page(c: canvas_module.Canvas, _doc):
#         # watermark first (behind everything)
#         _draw_watermark_full_area(c)

#         # header
#         _draw_header(c)

#         # small meta line under header
#         c.saveState()
#         c.setFillColor(colors.black)
#         c.setFont("Helvetica", 9)
#         try:
#             submitted_str = app.created_at.strftime("%Y-%m-%d %H:%M")
#         except Exception:
#             submitted_str = "-"
#         c.drawRightString(
#             page_w - 1.6 * cm,
#             page_h - HEADER_H - 0.65 * cm,
#             f"Application ID: {app.id} | Submitted: {submitted_str}",
#         )
#         c.restoreState()

#         # footer
#         _draw_footer(c)

#     # ------------------------------------------------------------
#     # CONTENT (ONLY ONCE - no duplication now)
#     # ------------------------------------------------------------
#     story = []

#     # Page 1
#     story.append(Paragraph("A) Organization Details", styles["SecTitle"]))
#     story.append(two_col_table([
#         ("Organization Name", getattr(app, "orgName", "")),
#         ("PAN (Entity)", getattr(app, "orgPAN", "")),
#         ("Registered Address", getattr(app, "orgAddress", "")),
#         ("Incorporation No", getattr(app, "incorpNo", "")),
#         ("Incorporation Date", getattr(app, "incorpDate", "")),
#         ("Nature of Business", getattr(app, "businessNature", "")),
#         ("GST No.", getattr(app, "gstNumber", "")),
#         ("Billing Address", getattr(app, "billingAddress", "")),
#         ("TAN No.", getattr(app, "tanNumber", "")),
#         ("Official Email", getattr(app, "orgEmail", "")),
#         ("Website", getattr(app, "orgWebsite", "")),
#         ("Contact No.", getattr(app, "orgContact", "")),
#         ("Alternate Contact No.", getattr(app, "orgAltContact", "")),
#     ]))
#     story.append(PageBreak())

#     # Page 2
#     story.append(Paragraph("B) Authorized Signatory Details", styles["SecTitle"]))
#     story.append(two_col_table([
#         ("Name", getattr(app, "authName", "")),
#         ("PAN", getattr(app, "authPAN", "")),
#         ("Designation", getattr(app, "authDesignation", "")),
#         ("DOB", getattr(app, "authDOB", "")),
#         ("Mobile", getattr(app, "authMobile", "")),
#         ("Email", getattr(app, "authEmail", "")),
#         ("Nationality", getattr(app, "authNationality", "")),
#         ("Correspondence Address", getattr(app, "correspondenceAddress", "")),
#         ("Authorization Letter Attached", yesno(getattr(app, "authLetter", False))),
#         ("ID Proof Attached", yesno(getattr(app, "idProof", False))),
#     ]))
#     story.append(Spacer(1, 10))
#     story.append(Paragraph("Uploaded Documents", styles["SecTitle"]))

#     docs_table = Table(
#         [
#             [p("<b>PAN Front</b>", "SmallC"), p("<b>PAN Back</b>", "SmallC")],
#             [img_cell(getattr(app, "authPanFront", None)), img_cell(getattr(app, "authPanBack", None))],
#             [p("<b>Aadhaar Front</b>", "SmallC"), p("<b>Aadhaar Back</b>", "SmallC")],
#             [img_cell(getattr(app, "authAadhaarFront", None)), img_cell(getattr(app, "authAadhaarBack", None))],
#         ],
#         colWidths=[8.2 * cm, 8.2 * cm],
#         hAlign="LEFT",
#     )
#     docs_table.setStyle(TableStyle([
#         ("BOX", (0, 0), (-1, -1), 0.9, colors.lightgrey),
#         ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
#         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#         ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#         ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
#         ("BACKGROUND", (0, 2), (-1, 2), colors.whitesmoke),
#         ("TOPPADDING", (0, 0), (-1, -1), 7),
#         ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
#     ]))
#     story.append(docs_table)
#     story.append(PageBreak())

#     # Page 3
#     story.append(Paragraph("C) Services + Confirmations", styles["SecTitle"]))
#     svc = services_list()
#     story.append(two_col_table([
#         ("Selected Services", ", ".join(svc) if svc else "-"),
#         ("Digital Requirements Confirmed", yesno(getattr(app, "digitalRequirements", False))),
#         ("Digital Key Notes Acknowledged", yesno(getattr(app, "digitalNotes", False))),
#         ("Communication Compliance Confirmed", yesno(getattr(app, "communicationCompliance", False))),
#         ("Terms & Conditions Accepted", yesno(getattr(app, "termsAgreement", False))),
#     ]))
#     story.append(PageBreak())

#     # Page 4
#     story.append(Paragraph("G) Undertaking", styles["SecTitle"]))
#     story.append(two_col_table([
#         ("Applicant Name", getattr(app, "applicantName", "")),
#         ("Applicant Date", getattr(app, "applicantDate", "")),
#         ("Company Signatory Name", getattr(app, "companySignatory", "")),
#         ("Company Date", getattr(app, "companyDate", "")),
#     ]))
#     story.append(Spacer(1, 10))
#     story.append(Paragraph("Signatures", styles["SecTitle"]))

#     applicant_sig = _safe_image_flowable(
#         getattr(app, "applicantSignatureFile", None),
#         width=7.5 * cm,
#         height=4.0 * cm
#     )

#     comp_img = None
#     if company_signature_path:
#         try:
#             comp_img = Image(company_signature_path, width=7.5 * cm, height=4.0 * cm)
#         except Exception:
#             comp_img = None

#     if comp_img is None:
#         comp_img = _safe_image_flowable(
#             getattr(app, "companySignatureFile", None),
#             width=7.5 * cm,
#             height=4.0 * cm
#         )

#     sig_table = Table(
#         [
#             [p("<b>For the Client (Applicant)</b>", "SmallC"), p("<b>For Click Connect Media Pvt. Ltd.</b>", "SmallC")],
#             [applicant_sig or p("<i>- Not provided -</i>", "SmallC"), comp_img or p("<i>- Not provided -</i>", "SmallC")],
#         ],
#         colWidths=[8.2 * cm, 8.2 * cm],
#         hAlign="LEFT",
#     )
#     sig_table.setStyle(TableStyle([
#         ("BOX", (0, 0), (-1, -1), 0.9, colors.lightgrey),
#         ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
#         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#         ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#         ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
#         ("TOPPADDING", (0, 0), (-1, -1), 8),
#         ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
#     ]))
#     story.append(sig_table)

#     # Build PDF (IMPORTANT: no canvas replay => no duplication)
#     doc.build(
#         story,
#         onFirstPage=_on_page,
#         onLaterPages=_on_page,
#     )

#     pdf = buf.getvalue()
#     buf.close()
#     return pdf


import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.pdfgen import canvas as canvas_module

# ------------------------------------------------------------
# THEME CONFIGURATION
# ------------------------------------------------------------
COMPANY_NAME = "Click Connect Media Pvt. Ltd."
COMPANY_TAGLINE = "Digital Marketing & Communication Services"
COMPANY_ADDR_LINES = [
    "Office No 301, B Wing, Kemp Plaza, Malad, Mindspace, Malad West",
    "Mumbai, Maharashtra 400064",
    "info@clickconnectmedia.in | www.clickconnectmedia.in",
    "+91 9892631244",
]

WATERMARK_TEXT = "Click Connect Media Pvt Ltd"
PRIMARY_DARK = colors.HexColor("#1A237E")  # Deep Navy Blue
ACCENT_BLUE = colors.HexColor("#00B0FF")   # Azure Accent
BG_LIGHT = colors.HexColor("#F8FAFC")      # Soft Surface Grey
WATERMARK_COLOR = colors.Color(0.10, 0.35, 0.75, alpha=0.07)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _exists_filefield(ff):
    try:
        return bool(ff) and bool(getattr(ff, "path", None))
    except Exception:
        return False

def _safe_image_flowable(file_field, width, height):
    try:
        if not _exists_filefield(file_field): return None
        return Image(file_field.path, width=width, height=height)
    except Exception: return None

def _wrap_text_to_width(c, text, max_width, font_name, font_size):
    if not text: return [""]
    c.saveState()
    c.setFont(font_name, font_size)
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font_name, font_size) <= max_width: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    c.restoreState()
    return lines

# ------------------------------------------------------------
# Builder
# ------------------------------------------------------------
def build_application_pdf(app, company_signature_path=None):
    buf = io.BytesIO()
    page_w, page_h = A4
    HEADER_H = 3.5 * cm
    FOOTER_H = 1.8 * cm

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=(HEADER_H + 1.5 * cm),
        bottomMargin=(FOOTER_H + 0.5 * cm)
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="GUITitle", fontSize=14, textColor=PRIMARY_DARK, fontName="Helvetica-Bold", spaceBefore=15, spaceAfter=12))
    styles.add(ParagraphStyle(name="Label", fontSize=9, textColor=colors.grey, fontName="Helvetica-Bold", alignment=TA_CENTER))

    def p(txt, style="Normal"):
        return Paragraph(str(txt if txt not in (None, "") else "-"), styles.get(style, styles["Normal"]))

    def yesno(v):
        return "Yes" if bool(v) else "No"

    def get_services():
        try:
            s = app.services_list()
            return s if s else []
        except Exception:
            csv = getattr(app, "services_csv", "") or ""
            return [x.strip() for x in csv.split(",") if x.strip()]

    def modern_gui_table(rows):
        data = []
        for k, v in rows:
            data.append([p(f"<b>{k}</b>"), p(v)])
        t = Table(data, colWidths=[6.2 * cm, 10.3 * cm], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG_LIGHT])
        ]))
        return t

    # ------------------------------------------------------------
    # Drawing Elements
    # ------------------------------------------------------------
    def _draw_chrome(c):
        # 1. PAGE BORDER
        c.saveState()
        c.setStrokeColor(PRIMARY_DARK)
        c.setLineWidth(2)
        c.rect(0.4 * cm, 0.4 * cm, page_w - 0.8 * cm, page_h - 0.8 * cm)
        c.setStrokeColor(ACCENT_BLUE)
        c.setLineWidth(0.5)
        c.rect(0.6 * cm, 0.6 * cm, page_w - 1.2 * cm, page_h - 1.2 * cm)
        c.restoreState()

        # 2. HEADER
        c.saveState()
        c.setFillColor(PRIMARY_DARK)
        c.rect(0.6 * cm, page_h - HEADER_H - 0.6 * cm, page_w - 1.2 * cm, HEADER_H, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(1.2 * cm, page_h - 1.8 * cm, COMPANY_NAME)
        c.setFont("Helvetica", 10)
        c.drawString(1.2 * cm, page_h - 2.4 * cm, COMPANY_TAGLINE.upper())
        
        c.setFont("Helvetica", 8)
        y_addr = page_h - 1.4 * cm
        for line in COMPANY_ADDR_LINES:
            c.drawRightString(page_w - 1.2 * cm, y_addr, line)
            y_addr -= 0.38 * cm
        c.restoreState()

        # 3. FOOTER
        c.saveState()
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(PRIMARY_DARK)
        c.drawString(1.2 * cm, 1.0 * cm, COMPANY_NAME)
        c.drawCentredString(page_w/2, 1.0 * cm, f"Official Business Record | ID: CCM-{app.id}")
        c.drawRightString(page_w - 1.2 * cm, 1.0 * cm, f"Page {c.getPageNumber()}")
        c.restoreState()

    def _draw_watermark(c):
        c.saveState()
        path = c.beginPath()
        path.rect(1 * cm, 2 * cm, page_w - 2 * cm, page_h - HEADER_H - 3 * cm)
        c.clipPath(path, stroke=0)
        c.setFillColor(WATERMARK_COLOR)
        c.setFont("Helvetica-Bold", 32)
        c.translate(page_w/2, page_h/2)
        c.rotate(45)
        for x in range(-2, 3):
            for y in range(-3, 4):
                c.drawCentredString(x * 14 * cm, y * 11 * cm, WATERMARK_TEXT)
        c.restoreState()

    def _on_page(c, _doc):
        _draw_chrome(c)
        _draw_watermark(c)

    # ------------------------------------------------------------
    # STORY ASSEMBLY (All Sections Preserved)
    # ------------------------------------------------------------
    story = []
    
    # Section A: Organization Details
    story.append(Paragraph("A) ORGANIZATION DETAILS", styles["GUITitle"]))
    story.append(modern_gui_table([
        ("Organization Name", getattr(app, "orgName", "")),
        ("PAN (Entity)", getattr(app, "orgPAN", "")),
        ("Registered Address", getattr(app, "orgAddress", "")),
        ("Incorporation No", getattr(app, "incorpNo", "")),
        ("Incorporation Date", getattr(app, "incorpDate", "")),
        ("Nature of Business", getattr(app, "businessNature", "")),
        ("GST No.", getattr(app, "gstNumber", "")),
        ("Billing Address", getattr(app, "billingAddress", "")),
        ("TAN No.", getattr(app, "tanNumber", "")),
        ("Official Email", getattr(app, "orgEmail", "")),
        ("Website", getattr(app, "orgWebsite", "")),
        ("Contact No.", getattr(app, "orgContact", "")),
        ("Alternate Contact No.", getattr(app, "orgAltContact", "")),
    ]))
    story.append(PageBreak())

    # Section B: Authorized Signatory Details
    story.append(Paragraph("B) AUTHORIZED SIGNATORY DETAILS", styles["GUITitle"]))
    story.append(modern_gui_table([
        ("Name", getattr(app, "authName", "")),
        ("PAN", getattr(app, "authPAN", "")),
        ("Designation", getattr(app, "authDesignation", "")),
        ("DOB", getattr(app, "authDOB", "")),
        ("Mobile", getattr(app, "authMobile", "")),
        ("Email", getattr(app, "authEmail", "")),
        ("Nationality", getattr(app, "authNationality", "")),
        ("Correspondence Address", getattr(app, "correspondenceAddress", "")),
        ("Authorization Letter Attached", yesno(getattr(app, "authLetter", False))),
        ("ID Proof Attached", yesno(getattr(app, "idProof", False))),
    ]))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("UPLOADED IDENTIFICATION DOCUMENTS", styles["GUITitle"]))
    def get_img(f):
        img = _safe_image_flowable(f, 7.5*cm, 4.2*cm)
        return img if img else p("<i>- Not provided -</i>", "Label")

    doc_grid = Table([
        [p("PAN FRONT", "Label"), p("PAN BACK", "Label")],
        [get_img(getattr(app, "authPanFront", None)), get_img(getattr(app, "authPanBack", None))],
        [p("AADHAAR FRONT", "Label"), p("AADHAAR BACK", "Label")],
        [get_img(getattr(app, "authAadhaarFront", None)), get_img(getattr(app, "authAadhaarBack", None))],
    ], colWidths=[8.5*cm, 8.5*cm])
    doc_grid.setStyle(TableStyle([
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (1,0), BG_LIGHT),
        ("BACKGROUND", (0,2), (1,2), BG_LIGHT),
    ]))
    story.append(doc_grid)
    story.append(PageBreak())

    # Section C: Services + Confirmations
    story.append(Paragraph("C) SERVICES + CONFIRMATIONS", styles["GUITitle"]))
    svc = get_services()
    story.append(modern_gui_table([
        ("Selected Services", ", ".join(svc) if svc else "-"),
        ("Digital Requirements Confirmed", yesno(getattr(app, "digitalRequirements", False))),
        ("Digital Key Notes Acknowledged", yesno(getattr(app, "digitalNotes", False))),
        ("Communication Compliance Confirmed", yesno(getattr(app, "communicationCompliance", False))),
        ("Terms & Conditions Accepted", yesno(getattr(app, "termsAgreement", False))),
    ]))
    story.append(PageBreak())

    # Section G: Undertaking
    story.append(Paragraph("G) UNDERTAKING", styles["GUITitle"]))
    story.append(modern_gui_table([
        ("Applicant Name", getattr(app, "applicantName", "")),
        ("Applicant Date", getattr(app, "applicantDate", "")),
        ("Company Signatory Name", getattr(app, "companySignatory", "")),
        ("Company Date", getattr(app, "companyDate", "")),
    ]))
    story.append(Spacer(1, 25))

    # Signatures GUI
    app_sig = _safe_image_flowable(getattr(app, "applicantSignatureFile", None), 7.0*cm, 3.5*cm)
    comp_sig = None
    if company_signature_path:
        try: comp_sig = Image(company_signature_path, 7.0*cm, 3.5*cm)
        except: pass
    if not comp_sig:
        comp_sig = _safe_image_flowable(getattr(app, "companySignatureFile", None), 7.0*cm, 3.5*cm)

    sig_row = Table([
        [p("FOR THE CLIENT (APPLICANT)", "Label"), p("FOR CLICK CONNECT MEDIA", "Label")],
        [app_sig or p("<i>- Not provided -</i>", "Label"), comp_sig or p("<i>- Not provided -</i>", "Label")]
    ], colWidths=[8.5*cm, 8.5*cm])
    sig_row.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1.2, PRIMARY_DARK),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(sig_row)

    # Build PDF
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    pdf_out = buf.getvalue()
    buf.close()
    return pdf_out