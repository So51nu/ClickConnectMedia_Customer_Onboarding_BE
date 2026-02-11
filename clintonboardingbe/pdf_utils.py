# pdf_utils.py
import io
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
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
# BRAND / THEME
# ------------------------------------------------------------
COMPANY_NAME = "Click Connect Media Pvt. Ltd."
COMPANY_TAGLINE = "Digital Marketing & Communication Services"
COMPANY_ADDR_LINES = [
    "Office No 301, B Wing, Kemp Plaza, Malad, Mindspace, Malad West",
    "Mumbai, Maharashtra 400064",
    "info@clickconnectmedia.in | www.clickconnectmedia.in",
    "+91 9892631244",
]

PRIMARY_DARK = colors.HexColor("#2B4056")
ACCENT_BLUE = colors.HexColor("#3FA9F5")
BG_LIGHT = colors.HexColor("#F4F6F9")
TEXT_DARK = colors.HexColor("#1F2937")
BORDER = colors.HexColor("#D1D5DB")

# ✅ PAGE BORDER: darker + bolder
PAGE_BORDER = colors.HexColor("#0B3D91")  # dark blue
PAGE_BORDER_W = 2.4                       # bold
PAGE_BORDER_INSET = 0.45 * cm             # inside-page inset (content stays inside)

WATERMARK_TEXT = "Click Connect Media Pvt Ltd"
WATERMARK_COLOR = colors.Color(0.10, 0.35, 0.75, alpha=0.06)


# ------------------------------------------------------------
# SERVICES (Checkbox + Routing)
# ------------------------------------------------------------
SERVICE_MASTER = [
    ("bulk-sms", "Bulk SMS"),
    ("bulk-whatsapp", "Bulk WhatsApp"),
    ("rcs-sms", "RCS SMS"),
    ("ivr-voice", "IVR Voice Calls"),
    ("social-media", "Social Media"),
    ("website-design", "Website Design / Development"),
    ("digital-marketing", "Digital Marketing (Meta/Google Ads)"),
    ("graphic-design", "Graphic Design"),
    ("paper-insert", "Paper Insert / Distribution"),
    ("seo-gmb", "SEO / GMB"),
]

DIGITAL_SET = {"digital-marketing", "social-media", "seo-gmb"}   # ✅ confirmed
COMM_SET = {"bulk-sms", "bulk-whatsapp", "rcs-sms", "ivr-voice"} # comm services
CREATIVE_SET = {"graphic-design", "paper-insert"}               # creative addendum
WEB_SET = {"website-design"}                                    # web addendum


# ------------------------------------------------------------
# CAF TEXT BLOCKS
# ------------------------------------------------------------
DIGITAL_REQ_BULLETS = [
    "Business details and approved brand assets (logo, colors, brand guidelines)",
    "Website / landing page URL and access for tracking setup (Pixel/GA4/GTM), if applicable",
    "Meta Business Manager and Ad Account access (Partner/Employee access)",
    "Google Ads account access, GA4/GSC access (if available) and Google Business Profile access (for Local/Maps)",
    "Verified domain/email and phone number for lead routing (Calls/WhatsApp/CRM)",
    "Service/product details, offer, location targeting, audience restrictions and negative list (if required)",
    "Compliance approvals for creatives and copy (claims, pricing, disclaimers, RERA where applicable)",
]

DIGITAL_DELIVERABLES_BULLETS = [
    "Campaign setup and structure aligned to objectives (Lead, Sales, Awareness, Traffic etc.)",
    "Creative and copy suggestions based on brand inputs and platform policies",
    "Tracking setup support (Pixel/GA4/GTM) based on access provided by Client",
    "Regular reporting on performance metrics, leads and optimization actions",
    "Optimization of targeting, placements, creatives and budget allocation as per trends",
]

DIGITAL_KEY_NOTES_BULLETS = [
    "Ad spend/budget is separate and payable by Client unless explicitly included in writing",
    "Platform approvals and results depend on policies, competition, audience behavior and market conditions",
    "Service Provider does not guarantee a fixed number of leads/sales/ROI or specific ranking positions",
    "Third-party tools (CRM, call tracking, landing pages, automation) if used may have separate costs",
]

COMM_SMS_BULLETS = [
    "DLT entity registration under the Client's legal entity (as per telecom norms)",
    "Approved Sender IDs/Headers and message templates registered on DLT before activation",
    "Client to provide required documents for DLT registration and verification (as applicable)",
    "Client shall ensure SMS is sent only to consented recipients and as per TRAI/DoT guidelines",
]

COMM_WA_BULLETS = [
    "Meta Business Manager access and business verification documents (if required by Meta)",
    "Display name and phone number onboarding; WABA setup as per Meta policies",
    "Template messages require pre-approval; templates must be compliant and non-misleading",
    "Strict opt-in: Client must maintain proof of user opt-in/consent and share it on request",
    "Opt-out mechanism: Client must honor STOP/UNSUBSCRIBE requests and update lists accordingly",
    "Conversation-based billing applies as per WhatsApp pricing policies (charged by Meta/partner)",
]

COMM_IVR_BULLETS = [
    "Calling database must be lawful and consent-based; unsolicited calls are prohibited",
    "Client must follow DND/scrubbing and calling time restrictions as per applicable rules",
    "Voice script/content must be approved by Client and must be compliant and non-deceptive",
    "Delivery depends on operator/network; call connect and pickup rates are not guaranteed",
]

COMM_RCS_BULLETS = [
    "Brand/agent setup and verification is mandatory (as per RCS platform requirements)",
    "Cards, carousels, buttons and rich templates are subject to platform approval and device/network availability",
    "Client must ensure content compliance and consent-based messaging",
    "Fallback to SMS may occur where RCS is not supported; billing applies accordingly",
]

OPTIN_BULLETS = [
    "Client confirms that recipient data is collected lawfully and with explicit consent (opt-in)",
    "Client shall maintain verifiable consent records (date/time/source) and share proof when required",
    "Client shall immediately remove recipients who opt-out and will not re-add without fresh consent",
    "Service Provider may suspend services if consent is doubtful or complaints/regulatory notices arise",
]


BASE_TERMS = [
    ("1. Scope of Services",
     "Services will be provided as per the mutually agreed scope in the proposal/email/invoice, including deliverables, timelines, and reporting format. Any change in scope will be treated as additional work and may require revised commercials and timelines."),
    ("2. Payments, Credits & Taxes",
     "Unless otherwise agreed in writing, services are on prepaid or advance payment basis. Payments once received are non-refundable after service initiation, approvals, or account setup."),
    ("3. Client Responsibilities",
     "Client shall provide accurate business details, documents, logos/brand assets, and timely approvals required for setup and execution. Delays in approvals or non-availability of required inputs may impact delivery timelines and outcomes."),
    ("4. Regulatory & Platform Compliance",
     "Client is solely responsible for ensuring that all content and communication sent through the services complies with applicable laws and regulations, including TRAI/DoT guidelines and platform policies (Meta/Google/WhatsApp)."),
    ("5. Delivery, Reporting & Third-Party Dependencies",
     "Delivery depends on operators, network availability, and third-party platform constraints; delays/outages beyond Service Provider control are not the Service Provider's liability."),
    ("6. Account Security & Confidentiality",
     "Client is responsible for securing login credentials, API keys, and access tokens; Service Provider is not liable for unauthorized use due to compromised credentials. Both parties shall maintain confidentiality of proprietary or sensitive information shared during the engagement."),
    ("7. Suspension, Termination & Refund Policy",
     "Either party may terminate this arrangement by giving 15 days written notice unless otherwise agreed in writing. No refund shall be provided for unused credits or partially delivered services after initiation."),
    ("8. Ownership & Data",
     "Client retains ownership of brand assets, content, and recipient data provided by the Client. Service Provider may retain system logs and billing records for compliance, audit, and dispute resolution purposes."),
    ("9. Data Protection & Consent Records",
     "Client shall maintain proper consent records for messaging/communication and ensure lawful processing of personal data. Service Provider may require proof of consent in case of complaints or regulatory queries."),
    ("10. Governing Law & Jurisdiction",
     "This arrangement shall be governed by the laws of India. Any dispute shall be subject to the exclusive jurisdiction of courts located in Mumbai, Maharashtra."),
]

DIGITAL_ADDENDUM = [
    ("Digital Marketing Disclaimer",
     "Service Provider does not guarantee a specific number of leads, sales, revenue, ROI, or ranking outcomes. Results depend on market conditions, audience behavior, offer attractiveness, landing page quality, and platform algorithm/policy changes."),
]
COMM_ADDENDUM = [
    ("Communication & Consent",
     "Client must ensure lawful and consent-based messaging/calling. Any misuse, spam complaints, DLT non-compliance, or policy violations may lead to suspension without refund and may attract regulatory action."),
]
WEB_ADDENDUM = [
    ("Website / Development Dependencies",
     "Delivery timelines depend on content, approvals, hosting/domain access, and third-party dependencies. Any additional pages/features beyond agreed scope will be billed separately."),
]
CREATIVE_ADDENDUM = [
    ("Creative / Artwork Approvals",
     "Creatives and copies will be shared for approval. Delays in approvals may impact publishing timelines. Revisions beyond agreed rounds may be chargeable."),
]


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
        if not _exists_filefield(file_field):
            return None
        return Image(file_field.path, width=width, height=height)
    except Exception:
        return None


def _wrap_text_to_width(c, text, max_width, font_name, font_size):
    if not text:
        return [""]
    c.saveState()
    c.setFont(font_name, font_size)
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font_name, font_size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    c.restoreState()
    return lines


def _sanitize(v):
    if v is None or v == "":
        return "-"
    return str(v)


def _yesno(v):
    return "Yes" if bool(v) else "No"


def _services_list(app):
    if hasattr(app, "services_list") and callable(getattr(app, "services_list")):
        try:
            s = app.services_list()
            if s:
                return [str(x).strip() for x in s if str(x).strip()]
        except Exception:
            pass
    csv = getattr(app, "services_csv", "") or ""
    return [x.strip() for x in csv.split(",") if x.strip()]


def _selected_groups(services):
    sset = set(services or [])
    return {
        "digital": bool(sset & DIGITAL_SET),
        "comm": bool(sset & COMM_SET),
        "creative": bool(sset & CREATIVE_SET),
        "web": bool(sset & WEB_SET),
    }


def _resolve_header_logo_path():
    try:
        from django.conf import settings
        mr = getattr(settings, "MEDIA_ROOT", None)
        if mr:
            p = os.path.join(mr, "image.png")
            if os.path.exists(p):
                return p
    except Exception:
        pass

    p2 = os.path.join(os.getcwd(), "media", "image.png")
    if os.path.exists(p2):
        return p2

    here = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.dirname(here)
    p3 = os.path.join(proj_root, "media", "image.png")
    if os.path.exists(p3):
        return p3

    return None


# ------------------------------------------------------------
# Builder
# ------------------------------------------------------------
def build_application_pdf(app, company_signature_path=None, company_stamp_path=None):
    buf = io.BytesIO()
    page_w, page_h = A4

    HEADER_H = 3.2 * cm
    FOOTER_H = 1.6 * cm

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=HEADER_H + 1.2 * cm,
        bottomMargin=FOOTER_H + 0.8 * cm,
        title="CAF - Click Connect Media",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="H1",
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=TEXT_DARK,
        spaceBefore=10,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="H2",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=TEXT_DARK,
        spaceBefore=8,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="P",
        fontName="Helvetica",
        fontSize=9.6,
        leading=12.2,
        textColor=TEXT_DARK,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Label",
        fontName="Helvetica-Bold",
        fontSize=8.4,
        leading=10.5,
        textColor=colors.grey,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Note",
        fontName="Helvetica",
        fontSize=9.2,
        leading=12,
        textColor=TEXT_DARK,
        backColor=BG_LIGHT,
        borderColor=BORDER,
        borderWidth=0.6,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=10,
    ))

    def P(txt, style="P"):
        return Paragraph(_sanitize(txt), styles[style])

    def bullets(items):
        return [Paragraph(f"• {_sanitize(b)}", styles["P"]) for b in items]

    def two_col_table(rows):
        data = []
        for k, v in rows:
            data.append([Paragraph(f"<b>{_sanitize(k)}</b>", styles["P"]),
                         Paragraph(_sanitize(v), styles["P"])])
        t = Table(data, colWidths=[6.4 * cm, 10.2 * cm], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.45, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    def checkbox_services_grid(selected):
        selected_set = set(selected or [])
        rows, row = [], []
        for key, label in SERVICE_MASTER:
            checked = "☑" if key in selected_set else "☐"
            row.append(Paragraph(f"{checked} {label}", styles["P"]))
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            row.append(Paragraph("", styles["P"]))
            rows.append(row)

        t = Table(rows, colWidths=[8.2 * cm, 8.2 * cm], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.45, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        return t

    # ------------------------------------------------------------
    # Header / Footer / Watermark / Border
    # ------------------------------------------------------------
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_logo_path = _resolve_header_logo_path()

    def _draw_page_border(c: canvas_module.Canvas):
        c.saveState()
        c.setStrokeColor(PAGE_BORDER)
        c.setLineWidth(PAGE_BORDER_W)
        inset = PAGE_BORDER_INSET
        c.rect(inset, inset, page_w - 2 * inset, page_h - 2 * inset, fill=0, stroke=1)
        c.restoreState()

    def _draw_header(c: canvas_module.Canvas):
        """
        ✅ Header is INSIDE border now (so top border visible)
        ✅ Overlap fixed
        """
        c.saveState()

        inset = PAGE_BORDER_INSET
        header_x = inset
        header_w = page_w - 2 * inset
        header_y = page_h - inset - HEADER_H

        # header bg inside border
        c.setFillColor(colors.white)
        c.rect(header_x, header_y, header_w, HEADER_H, fill=1, stroke=0)

        # layout inside header
        left_margin = header_x + 0.55 * cm
        right_margin = header_x + header_w - 0.55 * cm

        addr_block_w = 6.1 * cm
        right_x = right_margin
        addr_left_x = right_x - addr_block_w

        # Logo box inside header
        logo_x = left_margin
        logo_box_w = 6.4 * cm
        logo_box_h = 2.6 * cm
        logo_y = header_y + (HEADER_H - logo_box_h) / 2

        if header_logo_path:
            try:
                c.drawImage(
                    header_logo_path,
                    logo_x,
                    logo_y,
                    width=logo_box_w,
                    height=logo_box_h,
                    preserveAspectRatio=True,
                    anchor="sw",
                    mask="auto",
                )
            except Exception:
                pass

        # middle text region (between logo and address)
        gap = 0.35 * cm
        text_left_x = logo_x + logo_box_w + gap
        text_right_limit = addr_left_x - gap
        text_region_w = max(1.0 * cm, text_right_limit - text_left_x)

        name_font = 18
        while name_font > 12 and c.stringWidth(COMPANY_NAME, "Helvetica-Bold", name_font) > text_region_w:
            name_font -= 1

        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", name_font)
        c.drawString(text_left_x, header_y + HEADER_H - 1.15 * cm, COMPANY_NAME)

        tag_font = 10
        while tag_font > 8 and c.stringWidth(COMPANY_TAGLINE, "Helvetica", tag_font) > text_region_w:
            tag_font -= 1

        c.setFont("Helvetica", tag_font)
        c.drawString(text_left_x, header_y + HEADER_H - 1.85 * cm, COMPANY_TAGLINE)

        # address
        c.setFont("Helvetica", 8.2)
        y = header_y + HEADER_H - 0.95 * cm
        for raw in COMPANY_ADDR_LINES:
            for ln in _wrap_text_to_width(c, raw, addr_block_w, "Helvetica", 8.2):
                c.drawRightString(right_x, y, ln)
                y -= 0.42 * cm

        # divider line (inside header)
        c.setStrokeColor(BORDER)
        c.setLineWidth(1)
        c.line(header_x + 0.55 * cm, header_y - 0.02 * cm, header_x + header_w - 0.55 * cm, header_y - 0.02 * cm)

        c.restoreState()

    def _draw_footer(c: canvas_module.Canvas):
        c.saveState()

        inset = PAGE_BORDER_INSET
        left_x = inset + 0.55 * cm
        right_x = page_w - inset - 0.55 * cm

        c.setStrokeColor(BORDER)
        c.setLineWidth(1)
        c.line(left_x, inset + 1.2 * cm, right_x, inset + 1.2 * cm)

        c.setFont("Helvetica", 8.2)
        c.setFillColor(colors.grey)
        c.drawString(left_x, inset + 0.65 * cm, COMPANY_NAME)
        c.drawCentredString(page_w / 2, inset + 0.65 * cm, f"Generated: {generated_at}")
        c.drawRightString(right_x, inset + 0.65 * cm, f"Page {c.getPageNumber()}")

        c.restoreState()

    def _draw_watermark(c: canvas_module.Canvas):
        c.saveState()

        inset = PAGE_BORDER_INSET
        clip_x = inset
        clip_y = inset + FOOTER_H
        clip_w = page_w - 2 * inset
        clip_h = page_h - 2 * inset - HEADER_H - FOOTER_H

        path = c.beginPath()
        path.rect(clip_x, clip_y, clip_w, clip_h)
        c.clipPath(path, stroke=0, fill=0)

        c.setFillColor(WATERMARK_COLOR)
        c.setFont("Helvetica-Bold", 26)
        c.translate(page_w / 2, page_h / 2)
        c.rotate(35)

        step_x = 9.0 * cm
        step_y = 5.0 * cm
        start_x, end_x = -page_w, page_w
        start_y, end_y = -page_h, page_h

        y = start_y
        while y <= end_y:
            x = start_x
            while x <= end_x:
                c.drawString(x, y, WATERMARK_TEXT)
                x += step_x
            y += step_y

        c.restoreState()

    def _on_page(c: canvas_module.Canvas, _doc):
        # ✅ draw everything first
        _draw_watermark(c)
        _draw_header(c)

        # meta line
        c.saveState()
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica", 8.8)
        try:
            submitted_str = app.created_at.strftime("%Y-%m-%d %H:%M")
        except Exception:
            submitted_str = "-"

        inset = PAGE_BORDER_INSET
        c.drawRightString(
            page_w - inset - 1.6 * cm,
            page_h - inset - HEADER_H - 0.55 * cm,
            f"Application ID: {app.id} | Submitted: {submitted_str}",
        )
        c.restoreState()

        _draw_footer(c)

        # ✅ border LAST so header fill never hides it
        _draw_page_border(c)

    # ------------------------------------------------------------
    # CONTENT (Dynamic)
    # ------------------------------------------------------------
    services = _services_list(app)
    groups = _selected_groups(services)
    sset = set(services)

    story = []

    story.append(Paragraph(
        "Version: Feb 2026 | Applicable to Digital Marketing and Communication Services",
        styles["Note"]
    ))

    story.append(Paragraph("A. ORGANIZATION DETAILS", styles["H1"]))
    story.append(two_col_table([
        ("Name of Organization", getattr(app, "orgName", "")),
        ("PAN (Entity)", getattr(app, "orgPAN", "")),
        ("Registered Address (Entity)", getattr(app, "orgAddress", "")),
        ("Incorporation Number", getattr(app, "incorpNo", "")),
        ("Incorporation Date", getattr(app, "incorpDate", "")),
        ("Nature of Business", getattr(app, "businessNature", "")),
        ("GST No.", getattr(app, "gstNumber", "")),
        ("Billing Address (with Pincode)", getattr(app, "billingAddress", "")),
        ("TAN No. (If applicable)", getattr(app, "tanNumber", "")),
        ("Official Email ID", getattr(app, "orgEmail", "")),
        ("Website", getattr(app, "orgWebsite", "")),
        ("Contact No.", getattr(app, "orgContact", "")),
        ("Alternate Contact No.", getattr(app, "orgAltContact", "")),
    ]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("B. AUTHORIZED SIGNATORY DETAILS", styles["H1"]))
    story.append(two_col_table([
        ("Full Name", getattr(app, "authName", "")),
        ("PAN", getattr(app, "authPAN", "")),
        ("Designation", getattr(app, "authDesignation", "")),
        ("Date of Birth", getattr(app, "authDOB", "")),
        ("Mobile No.", getattr(app, "authMobile", "")),
        ("Email ID", getattr(app, "authEmail", "")),
        ("Nationality", getattr(app, "authNationality", "")),
        ("Correspondence Address", getattr(app, "correspondenceAddress", "")),
        ("Authorization Letter Attached", _yesno(getattr(app, "authLetter", False))),
        ("ID Proof Attached", _yesno(getattr(app, "idProof", False))),
    ]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("UPLOADED IDENTIFICATION DOCUMENTS", styles["H2"]))

    def img_cell(file_field):
        img = _safe_image_flowable(file_field, width=7.8 * cm, height=4.4 * cm)
        return img if img else Paragraph("<i>- Not provided -</i>", styles["Label"])

    doc_grid = Table([
        [Paragraph("PAN FRONT", styles["Label"]), Paragraph("PAN BACK", styles["Label"])],
        [img_cell(getattr(app, "authPanFront", None)), img_cell(getattr(app, "authPanBack", None))],
        [Paragraph("AADHAAR FRONT", styles["Label"]), Paragraph("AADHAAR BACK", styles["Label"])],
        [img_cell(getattr(app, "authAadhaarFront", None)), img_cell(getattr(app, "authAadhaarBack", None))],
    ], colWidths=[8.3 * cm, 8.3 * cm], hAlign="LEFT")
    doc_grid.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.45, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT),
        ("BACKGROUND", (0, 2), (-1, 2), BG_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(doc_grid)
    story.append(PageBreak())

    story.append(Paragraph("C. SERVICE DETAILS", styles["H1"]))
    story.append(Paragraph(
        "Tick the services opted (multiple selections allowed). Commercial terms (pricing, validity, scope and timelines) "
        "shall be as per the final proposal / email / invoice shared with the Client.",
        styles["P"]
    ))
    story.append(Spacer(1, 6))
    story.append(checkbox_services_grid(services))
    story.append(Spacer(1, 10))
    story.append(two_col_table([
        ("Selected Services", ", ".join(services) if services else "-"),
    ]))
    story.append(PageBreak())

    if groups["digital"]:
        story.append(Paragraph("D. DIGITAL MARKETING CAF (Meta / Google / SMM / SEO)", styles["H1"]))
        story.append(P(
            "This section applies to performance marketing and organic marketing services (Meta Ads, Google Ads, Social Media Management and SEO)."
        ))
        story.append(Paragraph("1) Client Requirements (Mandatory)", styles["H2"]))
        story.extend(bullets(DIGITAL_REQ_BULLETS))
        story.append(Spacer(1, 8))

        story.append(Paragraph("2) Our Deliverables (Execution & Reporting)", styles["H2"]))
        story.extend(bullets(DIGITAL_DELIVERABLES_BULLETS))
        story.append(Spacer(1, 8))

        story.append(Paragraph("3) Key Notes (Ads & Results)", styles["H2"]))
        story.extend(bullets(DIGITAL_KEY_NOTES_BULLETS))

        story.append(Spacer(1, 10))
        story.append(two_col_table([
            ("Client confirms requirements will be provided", _yesno(getattr(app, "digitalRequirements", False))),
            ("Client acknowledges key notes", _yesno(getattr(app, "digitalNotes", False))),
        ]))
        story.append(PageBreak())

    if groups["comm"]:
        story.append(Paragraph(
            "E. BULK SMS / WHATSAPP / IVR / RCS CAF (DLT, Templates, Opt-in & Compliance)",
            styles["H1"]
        ))
        story.append(P(
            "This section applies to communication services. Requirements are stricter due to telecom and platform regulations."
        ))

        if "bulk-sms" in sset:
            story.append(Paragraph("1) SMS (DLT) Requirements", styles["H2"]))
            story.extend(bullets(COMM_SMS_BULLETS))
            story.append(Spacer(1, 6))

        if "bulk-whatsapp" in sset:
            story.append(Paragraph("2) WhatsApp Business (Official API) Requirements", styles["H2"]))
            story.extend(bullets(COMM_WA_BULLETS))
            story.append(Spacer(1, 6))

        if "ivr-voice" in sset:
            story.append(Paragraph("3) IVR / Voice Calls Requirements", styles["H2"]))
            story.extend(bullets(COMM_IVR_BULLETS))
            story.append(Spacer(1, 6))

        if "rcs-sms" in sset:
            story.append(Paragraph("4) RCS Messaging Requirements", styles["H2"]))
            story.extend(bullets(COMM_RCS_BULLETS))
            story.append(Spacer(1, 6))

        story.append(Paragraph("5) Opt-in / Consent Undertaking", styles["H2"]))
        story.extend(bullets(OPTIN_BULLETS))
        story.append(Spacer(1, 10))

        story.append(two_col_table([
            ("Client confirms communication compliance", _yesno(getattr(app, "communicationCompliance", False))),
        ]))
        story.append(PageBreak())

    story.append(Paragraph("TERMS & CONDITIONS", styles["H1"]))
    story.append(P(
        "The below terms are applicable only to the services selected by the Client in this CAF (along with the base terms)."
    ))
    story.append(Spacer(1, 6))

    for title, body in BASE_TERMS:
        story.append(Paragraph(title, styles["H2"]))
        story.append(P(body))

    if groups["digital"]:
        for title, body in DIGITAL_ADDENDUM:
            story.append(Paragraph(title, styles["H2"]))
            story.append(P(body))

    if groups["comm"]:
        for title, body in COMM_ADDENDUM:
            story.append(Paragraph(title, styles["H2"]))
            story.append(P(body))

    if groups["web"]:
        for title, body in WEB_ADDENDUM:
            story.append(Paragraph(title, styles["H2"]))
            story.append(P(body))

    if groups["creative"]:
        for title, body in CREATIVE_ADDENDUM:
            story.append(Paragraph(title, styles["H2"]))
            story.append(P(body))

    story.append(Spacer(1, 8))
    story.append(two_col_table([
        ("Client accepts Terms & Conditions", _yesno(getattr(app, "termsAgreement", False))),
    ]))
    story.append(PageBreak())

    story.append(Paragraph("CUSTOMER UNDERTAKING", styles["H1"]))
    story.append(P(
        "By signing below, the Client confirms that the information provided in this CAF is true and accurate, and accepts all financial and legal responsibilities arising from the services."
    ))
    story.append(Spacer(1, 10))

    applicant_sig = _safe_image_flowable(getattr(app, "applicantSignatureFile", None), 7.0 * cm, 3.2 * cm)

    comp_sig = None
    if company_signature_path:
        try:
            comp_sig = Image(company_signature_path, width=7.0 * cm, height=3.2 * cm)
        except Exception:
            comp_sig = None
    if comp_sig is None:
        comp_sig = _safe_image_flowable(getattr(app, "companySignatureFile", None), 7.0 * cm, 3.2 * cm)

    def _img_or_placeholder(img):
        return img if img else Paragraph("<i>- Not provided -</i>", styles["Label"])

    sig_table = Table(
        [
            [Paragraph("<b>For the Client (Applicant)</b>", styles["P"]),
             Paragraph("<b>For Click Connect Media Pvt. Ltd.</b>", styles["P"])],
            [_img_or_placeholder(applicant_sig), _img_or_placeholder(comp_sig)],
            [Paragraph(f"<b>Name:</b> {_sanitize(getattr(app, 'applicantName', ''))}", styles["P"]),
             Paragraph(f"<b>Authorized Signatory:</b> {_sanitize(getattr(app, 'companySignatory', ''))}", styles["P"])],
            [Paragraph(f"<b>Date:</b> {_sanitize(getattr(app, 'applicantDate', ''))}", styles["P"]),
             Paragraph(f"<b>Date:</b> {_sanitize(getattr(app, 'companyDate', ''))}", styles["P"])],
        ],
        colWidths=[8.2 * cm, 8.2 * cm],
        hAlign="LEFT",
        repeatRows=1,
        splitByRow=1,
    )
    sig_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.45, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT),
        ("ALIGN", (0, 1), (-1, 1), "CENTER"),
    ]))
    story.append(sig_table)

    stamp_img = None
    if company_stamp_path:
        try:
            stamp_img = Image(company_stamp_path, width=6.0 * cm, height=6.0 * cm)
        except Exception:
            stamp_img = None

    if stamp_img:
        story.append(Spacer(1, 14))
        stamp_wrap = Table([[stamp_img]], colWidths=[16.4 * cm], hAlign="CENTER")
        stamp_wrap.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(stamp_wrap)
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Company Stamp</b>", styles["Label"]))

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)

    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
