#!/usr/bin/env python3
"""Generate SysManage Overview Presentation (PPTX)."""

import os
import cairosvg
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Paths ──────────────────────────────────────────────────────────────
DOCS_DIR = os.path.expanduser("~/dev/sysmanage-docs")
ASSETS_DIR = os.path.join(DOCS_DIR, "assets", "images")
OUT_DIR = os.path.join(DOCS_DIR, "Presentations")
OUT_FILE = os.path.join(OUT_DIR, "SysManage.pptx")

LOGO_SVG = os.path.join(ASSETS_DIR, "sysmanage-logo.svg")
ICON_SVG = os.path.join(ASSETS_DIR, "sysmanage-icon.svg")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PNG = os.path.join(SCRIPT_DIR, "sysmanage-logo.png")
ICON_PNG = os.path.join(SCRIPT_DIR, "sysmanage-icon.png")

# ── Branding colors ───────────────────────────────────────────────────
PRIMARY_BLUE = RGBColor(0x19, 0x76, 0xD2)
DARK_BLUE = RGBColor(0x0D, 0x3D, 0x5C)
GREEN = RGBColor(0x38, 0x8E, 0x3C)
BUTTON_GREEN = RGBColor(0x2E, 0x7D, 0x47)
DARK_TEXT = RGBColor(0x1A, 0x23, 0x32)
LIGHT_BG = RGBColor(0xF5, 0xF6, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MEDIUM_GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_BLUE = RGBColor(0xBB, 0xDE, 0xFB)
VERY_LIGHT_BLUE = RGBColor(0xE3, 0xF2, 0xFD)

FONT = "Arial"

# ── Slide dimensions (16:9) ───────────────────────────────────────────
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# ── Helpers ────────────────────────────────────────────────────────────

def convert_svgs():
    """Convert SVG logos to PNG for embedding."""
    cairosvg.svg2png(url=LOGO_SVG, write_to=LOGO_PNG, output_width=660, output_height=180)
    cairosvg.svg2png(url=ICON_SVG, write_to=ICON_PNG, output_width=360, output_height=360)


def add_dark_bg(slide):
    """Fill the entire slide with DARK_BLUE background."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BLUE


def add_light_bg(slide):
    """Fill the slide with light background."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = LIGHT_BG


def add_bottom_bar(slide):
    """Add a thin branded bar at the bottom of the slide."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), SLIDE_H - Inches(0.35),
        SLIDE_W, Inches(0.35),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = DARK_BLUE
    shape.line.fill.background()


def add_top_bar(slide):
    """Add a branded header bar at top."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        SLIDE_W, Inches(1.1),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = DARK_BLUE
    shape.line.fill.background()


def add_footer_text(slide, text="SysManage  |  sysmanage.org"):
    """Add small footer text in the bottom bar."""
    txBox = slide.shapes.add_textbox(
        Inches(0.5), SLIDE_H - Inches(0.33),
        Inches(6), Inches(0.3),
    )
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(9)
    p.font.color.rgb = WHITE
    p.font.name = FONT


def set_run(paragraph, text, size=18, bold=False, color=DARK_TEXT, font=FONT):
    """Add a run with formatting to a paragraph."""
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    return run


def add_title_textbox(slide, text, left=0.8, top=0.15, width=11, height=0.8,
                      size=36, color=WHITE, bold=True):
    """Add a title text in the header bar area."""
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    set_run(p, text, size=size, bold=bold, color=color)
    return tf


def add_body_textbox(slide, left=0.8, top=1.4, width=11.5, height=5.2):
    """Add a textbox for body content."""
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    return tf


def add_bullet_slide(slide, title, bullets, sub_bullets=None):
    """Standard content slide with header bar, title, bullets, footer."""
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, title)
    add_bottom_bar(slide)
    add_footer_text(slide)

    tf = add_body_textbox(slide)
    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(6)
        p.space_after = Pt(4)
        p.level = 0
        set_run(p, f"\u2022  {bullet}", size=18, color=DARK_TEXT)

        # Add sub-bullets if provided for this index
        if sub_bullets and i in sub_bullets:
            for sb in sub_bullets[i]:
                sp = tf.add_paragraph()
                sp.space_before = Pt(2)
                sp.space_after = Pt(2)
                sp.level = 1
                set_run(sp, f"    \u2013  {sb}", size=15, color=MEDIUM_GRAY)


def add_table_slide(slide, title, headers, rows, col_widths=None):
    """Content slide with a styled table."""
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, title)
    add_bottom_bar(slide)
    add_footer_text(slide)

    n_rows = len(rows) + 1
    n_cols = len(headers)
    left = Inches(0.8)
    top = Inches(1.5)
    width = Inches(11.5)
    height = Inches(0.4 * n_rows)

    table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    table = table_shape.table

    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = Inches(w)

    # Header row
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(14)
            paragraph.font.bold = True
            paragraph.font.color.rgb = WHITE
            paragraph.font.name = FONT

    # Data rows
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r % 2 == 1 else VERY_LIGHT_BLUE
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(13)
                paragraph.font.color.rgb = DARK_TEXT
                paragraph.font.name = FONT


def add_accent_rect(slide, left, top, width, height, color=PRIMARY_BLUE):
    """Add a colored rectangle accent."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_text_in_shape(shape, text, size=14, color=WHITE, bold=False, alignment=PP_ALIGN.CENTER):
    """Put text inside a shape."""
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = alignment
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.name = FONT


def add_multiline_in_shape(shape, lines, size=12, color=WHITE, bold=False,
                           alignment=PP_ALIGN.LEFT):
    """Put multiple lines of text inside a shape."""
    tf = shape.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = alignment
        p.space_before = Pt(2)
        p.space_after = Pt(2)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.name = FONT


# ── Slide Builders ─────────────────────────────────────────────────────

def slide_01_title(prs):
    """Title slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_dark_bg(slide)

    # Logo
    slide.shapes.add_picture(LOGO_PNG, Inches(4.0), Inches(1.0), Inches(5.3))

    # Main title
    txBox = slide.shapes.add_textbox(Inches(1.5), Inches(3.0), Inches(10), Inches(1.2))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p, "Cross-Platform System Management", size=32, bold=True, color=WHITE)

    # Tagline
    txBox2 = slide.shapes.add_textbox(Inches(2), Inches(4.2), Inches(9), Inches(0.8))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    set_run(p2, "Manage every host, every OS, from one platform.", size=20, color=LIGHT_BLUE)

    # Date
    txBox3 = slide.shapes.add_textbox(Inches(3), Inches(5.3), Inches(7), Inches(0.6))
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    set_run(p3, "February 2026", size=16, color=MEDIUM_GRAY)

    # Accent line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(5.0), Inches(5.0), Inches(3.3), Inches(0.04),
    )
    line.fill.solid()
    line.fill.fore_color.rgb = PRIMARY_BLUE
    line.line.fill.background()


def slide_02_agenda(prs):
    """Agenda slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Agenda")
    add_bottom_bar(slide)
    add_footer_text(slide)

    items = [
        ("Overview", "What is SysManage & architecture", "~10 min"),
        ("Features", "Open source + Pro+ capabilities", "~8 min"),
        ("Security", "Security-first design & dev process", "~5 min"),
        ("Live Demo", "Hands-on walkthrough", "~30 min"),
        ("Futures", "Roadmap to v3.0.0.0", "~5 min"),
        ("Recap", "Key takeaways & resources", "~2 min"),
    ]

    for i, (label, desc, time) in enumerate(items):
        y = 1.5 + i * 0.9
        # Number circle
        circ = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(1.2), Inches(y), Inches(0.55), Inches(0.55),
        )
        circ.fill.solid()
        circ.fill.fore_color.rgb = PRIMARY_BLUE
        circ.line.fill.background()
        add_text_in_shape(circ, str(i + 1), size=16, color=WHITE, bold=True)

        # Label
        txBox = slide.shapes.add_textbox(Inches(2.0), Inches(y), Inches(3), Inches(0.35))
        tf = txBox.text_frame
        set_run(tf.paragraphs[0], label, size=20, bold=True, color=DARK_BLUE)

        # Description
        txBox2 = slide.shapes.add_textbox(Inches(2.0), Inches(y + 0.32), Inches(5), Inches(0.3))
        tf2 = txBox2.text_frame
        set_run(tf2.paragraphs[0], desc, size=14, color=MEDIUM_GRAY)

        # Time badge
        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(10.0), Inches(y + 0.05), Inches(1.3), Inches(0.4),
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = VERY_LIGHT_BLUE
        badge.line.fill.background()
        add_text_in_shape(badge, time, size=12, color=DARK_BLUE, bold=True)


def slide_03_problem(prs):
    """The Problem slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "Heterogeneous OS estates \u2014 Linux, macOS, Windows, *BSD all in one environment",
        "Security & compliance requirements \u2014 SOC2, HIPAA, FedRAMP, CIS, DISA STIG",
        "Agent sprawl \u2014 separate tools for monitoring, patching, compliance, secrets",
        "Manual toil \u2014 SSH loops, ad-hoc scripts, no audit trail",
        "No single pane of glass \u2014 context-switching between dashboards",
        "Commercial lock-in \u2014 expensive per-host licensing with opaque code",
    ]
    add_bullet_slide(slide, "The Problem", bullets)


def slide_04_what_is(prs):
    """What is SysManage? slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "What is SysManage?")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Left column: description
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(6.5), Inches(5.0))
    tf = txBox.text_frame
    tf.word_wrap = True

    items = [
        ("Server + Agent architecture", "Central server manages distributed agents on every host"),
        ("Real-time WebSocket communication", "Live metrics, status updates, and command execution"),
        ("FastAPI backend + React frontend", "Modern Python API with responsive web UI"),
        ("PostgreSQL database", "Reliable, scalable data store for all host & config data"),
        ("AGPLv3 open source core", "Transparent, auditable, community-driven"),
        ("Pro+ commercial modules", "Enterprise features with Cython-compiled add-ons"),
    ]

    for i, (title, desc) in enumerate(items):
        if i > 0:
            p = tf.add_paragraph()
            p.space_before = Pt(10)
        else:
            p = tf.paragraphs[0]
            p.space_before = Pt(4)
        set_run(p, f"\u2022  {title}", size=17, bold=True, color=DARK_BLUE)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        set_run(p2, f"     {desc}", size=14, color=MEDIUM_GRAY)

    # Right column: icon
    slide.shapes.add_picture(ICON_PNG, Inches(9.0), Inches(2.0), Inches(3.0))


def slide_05_who_bryan(prs):
    """Who is SysManage? — Bryan Everly slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Who is SysManage? \u2014 Bryan Everly")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Role badge
    badge = add_accent_rect(slide, 0.8, 1.35, 3.0, 0.5, PRIMARY_BLUE)
    add_text_in_shape(badge, "Founder & CEO", size=16, color=WHITE, bold=True)

    # Career timeline
    career = [
        ("Software Artistry", "Early employee \u2192 Dir. of Worldwide Product Dev  \u2022  IPO 1995  \u2022  Sold to IBM/Tivoli 1998"),
        ("IBM", "Led global engineering team post-acquisition (3 years)"),
        ("SaaS Founder", "Founded & sold a SaaS company securing sensitive HR data (~8 years)"),
        ("ExactTarget", "Engineering leader (1/3 of technology team)  \u2022  Later acquired by Salesforce"),
        ("Aprimo / Teradata", "VP of Worldwide Engineering  \u2022  $525M acquisition by Teradata"),
        ("NextGear Capital", "CTO  \u2022  Built dev org from scratch  \u2022  Grew loan volume $1.6B \u2192 $3.2B  \u2022  CTO of the Year (IBJ/TechPoint)"),
        ("Cox Automotive", "CTO & CISO"),
        ("Cummins", "Chief Enterprise Architect & Exec. Dir. Software Engineering"),
        ("Canonical", "VP of Software Engineering  \u2022  Ubuntu, IoT, real-time Linux, HPC"),
    ]

    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.5), Inches(4.5))
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, (company, detail) in enumerate(career):
        if i > 0:
            p = tf.add_paragraph()
            p.space_before = Pt(6)
        else:
            p = tf.paragraphs[0]
            p.space_before = Pt(2)
        set_run(p, f"{company}  ", size=15, bold=True, color=DARK_BLUE)
        set_run(p, f"\u2014  {detail}", size=13, bold=False, color=MEDIUM_GRAY)

    # Education & OSS footer
    txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11.5), Inches(0.5))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    set_run(tf2.paragraphs[0],
            "M.S. Cybersecurity, UC Berkeley  \u2022  B.S. Computer Science, Indiana State  \u2022  OpenBSD Ports Maintainer",
            size=12, color=DARK_TEXT)


def slide_06_who_fedor(prs):
    """Who is SysManage? — Fedor Dikarev slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Who is SysManage? \u2014 Fedor Dikarev")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Role badge
    badge = add_accent_rect(slide, 0.8, 1.35, 4.5, 0.5, PRIMARY_BLUE)
    add_text_in_shape(badge, "Lead SRE / CI/CD Engineer", size=16, color=WHITE, bold=True)

    # Background items
    items = [
        ("Databricks (via Neon acquisition)",
         "Infrastructure engineer at Databricks following the ~$1B acquisition of Neon, the serverless Postgres company"),
        ("Neon \u2014 Serverless Postgres",
         "Member of Technical Staff  \u2022  Led CI/CD infrastructure migration and cost optimization  \u2022  Reduced cloud CI costs by 50%"),
        ("Infrastructure & DevOps Expertise",
         "Deep experience with AWS, Docker, Kubernetes, Prometheus monitoring, and high-availability architectures"),
        ("CI/CD & Automation",
         "Designed and operated large-scale continuous integration pipelines  \u2022  GitHub Actions, ephemeral runners, caching optimization"),
        ("Open Source Contributor",
         "Active GitHub contributor  \u2022  Published tools for AWS HA, Docker Swarm service registration, and Prometheus metrics"),
        ("Based in Germany",
         "Bringing European engineering perspective and timezone coverage to the team"),
    ]

    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(11.5), Inches(4.2))
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, (title, desc) in enumerate(items):
        if i > 0:
            p = tf.add_paragraph()
            p.space_before = Pt(10)
        else:
            p = tf.paragraphs[0]
            p.space_before = Pt(4)
        set_run(p, f"\u2022  {title}", size=16, bold=True, color=DARK_BLUE)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        set_run(p2, f"     {desc}", size=13, color=MEDIUM_GRAY)


def slide_07_growth_strategy(prs):
    """Growth Strategy — VC & Advisors slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Growth Strategy")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # VC box
    vc_box = add_accent_rect(slide, 0.8, 1.5, 5.5, 3.0, DARK_BLUE)
    add_multiline_in_shape(vc_box, [
        "Venture Capital",
        "",
        "In active discussions with a European",
        "venture capital fund focused on open",
        "source and infrastructure software",
    ], size=14, color=WHITE, alignment=PP_ALIGN.LEFT)

    # Advisors box
    adv_box = add_accent_rect(slide, 7.0, 1.5, 5.5, 3.0, PRIMARY_BLUE)
    add_multiline_in_shape(adv_box, [
        "Advisory Network",
        "",
        "Engaging potential advisors from",
        "proven open source \u2192 commercial",
        "success stories including NGINX",
        "and WordPress ecosystems",
    ], size=14, color=WHITE, alignment=PP_ALIGN.LEFT)

    # Bottom: strategy note
    strategy_box = add_accent_rect(slide, 0.8, 5.0, 11.7, 1.5, BUTTON_GREEN)
    add_multiline_in_shape(strategy_box, [
        "Open Source \u2192 Commercial Playbook",
        "",
        "AGPLv3 core builds community trust & adoption  \u2192  Pro+ tiers monetize enterprise needs",
        "Following the proven model: open core + commercial extensions + enterprise support",
    ], size=13, color=WHITE, alignment=PP_ALIGN.CENTER)


def slide_08_architecture(prs):
    """Architecture Diagram slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Architecture")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Server box
    server_box = add_accent_rect(slide, 4.5, 1.8, 4.3, 2.8, DARK_BLUE)
    add_multiline_in_shape(server_box, [
        "SysManage Server",
        "",
        "FastAPI Backend",
        "React Frontend",
        "WebSocket Engine",
    ], size=13, bold=False, color=WHITE, alignment=PP_ALIGN.CENTER)

    # PostgreSQL
    db_box = add_accent_rect(slide, 4.5, 5.2, 4.3, 0.8, PRIMARY_BLUE)
    add_text_in_shape(db_box, "PostgreSQL Database", size=14, color=WHITE, bold=True)

    # Agent boxes (left and right)
    for x_pos in [0.8, 9.5]:
        agent_box = add_accent_rect(slide, x_pos, 2.2, 2.8, 1.8, GREEN)
        add_multiline_in_shape(agent_box, [
            "SysManage Agent",
            "",
            "Local DB (SQLite)",
            "System Metrics",
        ], size=12, color=WHITE, alignment=PP_ALIGN.CENTER)

    # mTLS labels
    for x_pos, label_x in [(3.8, 3.0), (8.8, 9.0)]:
        txBox = slide.shapes.add_textbox(Inches(label_x), Inches(2.5), Inches(1.5), Inches(0.4))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p, "mTLS\n\u2194", size=12, bold=True, color=PRIMARY_BLUE)

    # Pro+ modules
    pro_box = add_accent_rect(slide, 9.5, 4.8, 2.8, 1.5, BUTTON_GREEN)
    add_multiline_in_shape(pro_box, [
        "Pro+ Modules",
        "Health \u2022 Compliance",
        "Reporting \u2022 Secrets",
        "Containers \u2022 CVE",
    ], size=11, color=WHITE, alignment=PP_ALIGN.CENTER)


def slide_09_cross_platform(prs):
    """Cross-Platform Matrix slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    headers = ["Operating System", "Server", "Agent"]
    rows = [
        ("Linux (Ubuntu, Debian, RHEL, Alpine, etc.)", "\u2713", "\u2713"),
        ("macOS (13+)", "\u2713", "\u2713"),
        ("Windows (10/11, Server 2019+)", "\u2713", "\u2713"),
        ("FreeBSD (13+)", "\u2713", "\u2713"),
        ("OpenBSD (7.4+)", "\u2713", "\u2713"),
        ("NetBSD (10+)", "\u2713", "\u2713"),
    ]
    add_table_slide(slide, "Cross-Platform Support", headers, rows,
                    col_widths=[6.0, 2.5, 2.5])


def slide_10_packaging(prs):
    """Packaging Formats & OS Versions slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    headers = ["Format", "OS / Distro", "Versions"]
    rows = [
        (".deb", "Ubuntu, Debian", "20.04+, Bookworm+"),
        (".rpm", "RHEL, Fedora, SUSE", "8+, 38+, 15+"),
        (".pkg", "macOS", "13 Ventura+"),
        (".msi", "Windows", "10/11, Server 2019+"),
        (".snap", "Ubuntu/Snapcraft", "Core 22+"),
        (".flatpak", "Linux (universal)", "Flathub"),
        (".apk", "Alpine Linux", "3.18+"),
        (".tgz", "FreeBSD", "13+"),
        ("port", "OpenBSD, NetBSD", "7.4+ / 10+"),
    ]
    add_table_slide(slide, "Packaging Formats & OS Versions", headers, rows,
                    col_widths=[2.0, 4.0, 4.0])


def slide_11_i18n(prs):
    """Internationalization slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Internationalization")
    add_bottom_bar(slide)
    add_footer_text(slide)

    languages = [
        ("English", "en"), ("French", "fr"), ("German", "de"),
        ("Spanish", "es"), ("Italian", "it"), ("Portuguese", "pt"),
        ("Dutch", "nl"), ("Russian", "ru"), ("Chinese (Simplified)", "zh"),
        ("Japanese", "ja"), ("Korean", "ko"), ("Hindi", "hi"),
        ("Arabic (RTL)", "ar"), ("Turkish", "tr"),
    ]

    cols = 3
    for i, (lang, code) in enumerate(languages):
        col = i % cols
        row = i // cols
        x = 1.0 + col * 4.0
        y = 1.6 + row * 0.8

        badge = add_accent_rect(slide, x, y, 3.4, 0.55, PRIMARY_BLUE if code != "ar" else GREEN)
        add_text_in_shape(badge, f"{lang}  ({code})", size=14, color=WHITE, bold=True)

    # Note
    txBox = slide.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(10), Inches(0.5))
    tf = txBox.text_frame
    set_run(tf.paragraphs[0], "Full UI + backend message localization  \u2022  RTL support for Arabic",
            size=14, color=MEDIUM_GRAY)


def slide_12_oss_features(prs):
    """Open Source Features slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "Host management \u2014 register, organize, tag, and monitor all hosts",
        "Software inventory \u2014 full package listing per host",
        "Update detection \u2014 identify available OS and package updates",
        "Package management \u2014 install, remove, upgrade packages remotely",
        "Repository management \u2014 configure package sources across hosts",
        "Certificate monitoring \u2014 track TLS certificate expiration dates",
        "Firewall & AV status \u2014 verify security posture at a glance",
        "Role-Based Access Control \u2014 Admin, Operator, Viewer roles",
        "User management \u2014 create, modify, deactivate user accounts",
        "Tagging system \u2014 flexible host categorization and filtering",
    ]
    add_bullet_slide(slide, "Open Source Features", bullets)


def slide_13_oss_monitoring(prs):
    """Open Source: Monitoring & Management slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "Real-time CPU, RAM, disk, and network metrics via WebSocket",
        "System uptime and last-seen tracking",
        "OS identification and version detection",
        "Storage inventory \u2014 partitions, mount points, usage",
        "Ubuntu Pro integration \u2014 ESM status and entitlements",
        "Host detail dashboard with at-a-glance health overview",
        "WebSocket-driven live updates \u2014 no polling, no page refresh",
    ]
    add_bullet_slide(slide, "Open Source: Monitoring & Management", bullets)


def slide_14_proplus_licensing(prs):
    """Pro+ Licensing Model slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Pro+ Licensing Model")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Professional tier box
    pro_box = add_accent_rect(slide, 0.8, 1.6, 5.5, 4.5, PRIMARY_BLUE)
    add_multiline_in_shape(pro_box, [
        "Professional Tier",
        "",
        "\u2022  Health Engine (AI-powered)",
        "\u2022  Compliance Engine (CIS/STIG)",
        "\u2022  Reporting Engine (PDF/HTML)",
        "\u2022  Audit Engine (tamper-evident)",
        "\u2022  Secrets Engine (OpenBAO)",
        "\u2022  Container Engine (LXD/WSL)",
        "\u2022  CVE Vulnerability Engine",
        "\u2022  Alerting Engine",
    ], size=14, color=WHITE, alignment=PP_ALIGN.LEFT)

    # Enterprise tier box
    ent_box = add_accent_rect(slide, 7.0, 1.6, 5.5, 4.5, DARK_BLUE)
    add_multiline_in_shape(ent_box, [
        "Enterprise Tier",
        "",
        "Everything in Professional, plus:",
        "",
        "\u2022  AV Management",
        "\u2022  Firewall Orchestration",
        "\u2022  Virtualization (KVM/bhyve/VMM)",
        "\u2022  Observability",
        "\u2022  Automation & Fleet",
        "\u2022  Air-Gapped Support",
        "\u2022  MFA",
    ], size=14, color=WHITE, alignment=PP_ALIGN.LEFT)

    # Bottom note
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11), Inches(0.5))
    tf = txBox.text_frame
    set_run(tf.paragraphs[0],
            "ECDSA P-521 license validation  \u2022  Feature gating  \u2022  Host count enforcement  \u2022  Cython-compiled modules",
            size=13, color=MEDIUM_GRAY)


def slide_15_proplus_professional(prs):
    """Pro+ Professional Tier slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "proplus_core \u2014 license validation, feature gating, module loader",
        "health_engine \u2014 AI-powered system health analysis and recommendations",
        "compliance_engine \u2014 CIS Benchmarks and DISA STIG auditing",
        "reporting_engine \u2014 PDF and HTML report generation",
        "audit_engine \u2014 tamper-evident audit logging with hash chains",
        "secrets_engine \u2014 OpenBAO-backed encrypted secrets management",
        "container_engine \u2014 LXD and WSL container management",
    ]
    add_bullet_slide(slide, "Pro+ Professional Tier", bullets)


def slide_16_proplus_enterprise(prs):
    """Pro+ Enterprise Tier slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "vuln_engine \u2014 CVE vulnerability scanning and tracking",
        "alerting_engine \u2014 Email, Webhook, Slack, and Teams notifications",
    ]
    sub = {
        2: [
            "AV management \u2014 centralized antivirus policy and status",
            "Firewall orchestration \u2014 cross-platform firewall rule management",
            "Virtualization \u2014 KVM, bhyve, VMM hypervisor management",
            "Observability \u2014 centralized log and metric aggregation",
            "Automation & Fleet \u2014 task scheduling and fleet-wide operations",
            "Air-gapped support \u2014 offline/disconnected environment management",
            "MFA \u2014 multi-factor authentication for the management console",
        ],
    }
    add_bullet_slide(slide, "Pro+ Enterprise Tier", bullets + ["Upcoming enterprise modules:"], sub)


def slide_17_ecosystem(prs):
    """Ecosystem Integrations slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Ecosystem Integrations")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Categories with integrations
    categories = [
        ("Secrets & Key Management", [
            ("OpenBAO / Vault", "Encrypted secrets storage, API keys, credential management"),
        ], DARK_BLUE),
        ("Observability", [
            ("OpenTelemetry", "Distributed tracing and metrics collection"),
            ("Grafana", "Dashboard visualization and metrics"),
            ("Prometheus", "Metrics collection and querying"),
            ("Graylog", "Centralized log aggregation (GELF, syslog)"),
        ], PRIMARY_BLUE),
        ("Vulnerability Data", [
            ("NIST NVD", "National Vulnerability Database (CVE)"),
            ("Ubuntu / Debian / Red Hat / Microsoft / FreeBSD", "OS-specific security advisories"),
        ], BUTTON_GREEN),
        ("Platform & Virtualization", [
            ("Ubuntu Pro", "ESM, security patching, compliance"),
            ("LXD / Incus", "Container management"),
            ("KVM / bhyve / VMM", "Hypervisor management"),
        ], GREEN),
        ("Notifications", [
            ("SMTP / Email", "Alert delivery"),
            ("Webhooks / Slack / Teams", "Real-time notifications"),
        ], DARK_BLUE),
        ("Firewalls", [
            ("UFW / iptables / nftables / PF", "Cross-platform firewall management"),
        ], PRIMARY_BLUE),
    ]

    y = 1.4
    for cat_name, items, color in categories:
        # Category header
        cat_box = add_accent_rect(slide, 0.8, y, 3.2, 0.4, color)
        add_text_in_shape(cat_box, cat_name, size=11, color=WHITE, bold=True)

        # Items
        for j, (name, desc) in enumerate(items):
            item_x = 4.3
            item_y = y + j * 0.4
            txBox = slide.shapes.add_textbox(
                Inches(item_x), Inches(item_y), Inches(8.5), Inches(0.38),
            )
            tf = txBox.text_frame
            tf.word_wrap = True
            set_run(tf.paragraphs[0], name, size=11, bold=True, color=DARK_BLUE)
            set_run(tf.paragraphs[0], f"  \u2014  {desc}", size=10, bold=False, color=MEDIUM_GRAY)

        row_height = max(len(items) * 0.4, 0.45)
        y += row_height + 0.12

    # Bottom note
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(11.5), Inches(0.4))
    tf = txBox.text_frame
    set_run(tf.paragraphs[0],
            "SysManage integrates \u2014 not replaces \u2014 best-of-breed tools in each category",
            size=12, bold=True, color=DARK_TEXT)


def slide_18_why_security(prs):
    """Why Security Matters slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "Privileged access to every managed host \u2014 a compromised management platform is catastrophic",
        "Credential store \u2014 secrets engine holds sensitive keys and passwords",
        "Attack surface amplification \u2014 one server connects to hundreds of agents",
        "Compliance mandates \u2014 SOC2, HIPAA, FedRAMP require secure management tooling",
        "Supply chain risk \u2014 management software is a high-value target",
        "Audit requirements \u2014 every action must be traceable and tamper-evident",
    ]
    add_bullet_slide(slide, "Why Security Matters for Systems Management", bullets)


def slide_19_security_architecture(prs):
    """Security-First Architecture slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "mTLS agent communication \u2014 mutual TLS for all server-agent traffic",
        "JWT authentication with rotation \u2014 short-lived tokens, automatic refresh",
        "No inbound agent ports \u2014 agents connect outbound only, reducing attack surface",
        "UUID primary keys \u2014 prevents enumeration attacks on API endpoints",
        "OpenBAO encrypted secrets \u2014 HashiCorp Vault-compatible secrets management",
        "ECDSA P-521 license signing \u2014 cryptographically secure license validation",
        "TLS 1.2+ enforced \u2014 no legacy protocol support",
        "Cython-compiled Pro+ modules \u2014 source code protection for commercial features",
    ]
    add_bullet_slide(slide, "Security-First Architecture", bullets)


def slide_20_security_devprocess(prs):
    """Security in the Development Process slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Security in the Development Process")
    add_bottom_bar(slide)
    add_footer_text(slide)

    tools = [
        ("Bandit", "Python security linter"),
        ("Semgrep Pro", "Static analysis rules"),
        ("SonarCloud", "Code quality & security"),
        ("CodeQL", "Semantic code analysis"),
        ("Safety", "Dependency vulnerability check"),
        ("Snyk", "Open source security scanning"),
        ("TruffleHog", "Secret detection in commits"),
        ("Black", "Deterministic code formatting"),
        ("PyLint 10/10", "Code quality enforcement"),
        ("Dependabot", "Automated dependency updates"),
        ("Pinned GH Actions", "SHA-pinned CI/CD actions"),
        ("Playwright", "End-to-end UI testing"),
    ]

    cols = 3
    for i, (tool, desc) in enumerate(tools):
        col = i % cols
        row = i // cols
        x = 0.8 + col * 4.0
        y = 1.5 + row * 1.2

        box = add_accent_rect(slide, x, y, 3.5, 0.9, PRIMARY_BLUE if i % 2 == 0 else DARK_BLUE)
        add_multiline_in_shape(box, [tool, desc], size=13, color=WHITE, alignment=PP_ALIGN.CENTER)


def slide_21_sbom(prs):
    """Software Bill of Materials (SBOM) slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Software Bill of Materials (SBOM)")
    add_bottom_bar(slide)
    add_footer_text(slide)

    # Left column: what & why
    left_box = add_accent_rect(slide, 0.8, 1.5, 5.5, 3.5, DARK_BLUE)
    add_multiline_in_shape(left_box, [
        "What & Why",
        "",
        "\u2022  CycloneDX JSON format (v1.6)",
        "\u2022  Full dependency inventory for every release",
        "\u2022  Supply chain transparency & auditability",
        "\u2022  Separate SBOMs for backend (Python)",
        "    and frontend (Node.js) components",
        "\u2022  Agent packages include their own SBOM",
    ], size=13, color=WHITE, alignment=PP_ALIGN.LEFT)

    # Right column: how & where
    right_box = add_accent_rect(slide, 7.0, 1.5, 5.5, 3.5, PRIMARY_BLUE)
    add_multiline_in_shape(right_box, [
        "Generation & Distribution",
        "",
        "\u2022  Automated via CI/CD on every build",
        "\u2022  cyclonedx-bom (Python dependencies)",
        "\u2022  @cyclonedx/cyclonedx-npm (Node.js)",
        "\u2022  Published as GitHub release artifacts",
        "\u2022  Bundled inside every installer",
        "    (.deb, .rpm, .msi, .pkg, .snap, .tgz, ...)",
    ], size=13, color=WHITE, alignment=PP_ALIGN.LEFT)

    # Bottom: compatibility note
    compat_box = add_accent_rect(slide, 0.8, 5.4, 11.7, 1.0, BUTTON_GREEN)
    add_multiline_in_shape(compat_box, [
        "Compatible with: Grype  \u2022  Trivy  \u2022  Dependency-Track  \u2022  Snyk",
        "Inspect locally:  jq . backend-sbom.json  |  jq '.components | length'",
    ], size=13, color=WHITE, alignment=PP_ALIGN.CENTER)


def slide_22_demo_sequence(prs):
    """Demo Sequence slide — numbered walkthrough of the demo."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Demo Sequence")
    add_bottom_bar(slide)
    add_footer_text(slide)

    steps = [
        ("1", "Dashboard & Host Overview", "Navigate the main dashboard, view registered hosts and status"),
        ("2", "Host Detail Deep-Dive", "Live CPU/RAM/disk/network metrics, OS info, uptime, storage"),
        ("3", "Software Inventory & Updates", "View installed packages, detect available updates"),
        ("4", "Package Management", "Install and remove a package remotely from the browser"),
        ("5", "User Management & RBAC", "Create a user, assign roles (Admin/Operator/Viewer)"),
        ("6", "Settings & Configuration", "Server configuration, agent settings, preferences"),
        ("7", "Multi-Language Switching", "Switch UI language live across supported locales"),
    ]

    pro_steps = [
        ("8", "Health Analysis", "AI-powered system health scoring and recommendations"),
        ("9", "Compliance Audit", "Run CIS Benchmark / DISA STIG checks against a host"),
        ("10", "PDF Report Generation", "Generate and download a formatted compliance report"),
        ("11", "Secrets Management", "Store and retrieve secrets via OpenBAO integration"),
        ("12", "Container Management", "View and manage LXD containers on a host"),
        ("13", "CVE Vulnerability Scan", "Scan host packages against the CVE database"),
        ("14", "Alerting Configuration", "Configure Email, Webhook, Slack, and Teams alerts"),
        ("15", "Audit Log", "Browse tamper-evident audit trail with hash chain verification"),
    ]

    # Open Source section header
    oss_label = slide.shapes.add_textbox(Inches(0.8), Inches(1.25), Inches(3), Inches(0.3))
    tf = oss_label.text_frame
    set_run(tf.paragraphs[0], "Open Source", size=14, bold=True, color=PRIMARY_BLUE)

    # Pro+ section header
    pro_label = slide.shapes.add_textbox(Inches(6.5), Inches(1.25), Inches(3), Inches(0.3))
    tf2 = pro_label.text_frame
    set_run(tf2.paragraphs[0], "Pro+", size=14, bold=True, color=BUTTON_GREEN)

    for col_idx, items in enumerate([steps, pro_steps]):
        x = 0.8 + col_idx * 5.7
        for i, (num, title, desc) in enumerate(items):
            y = 1.55 + i * 0.68

            # Step number circle
            circ = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(x), Inches(y), Inches(0.38), Inches(0.38),
            )
            color = PRIMARY_BLUE if col_idx == 0 else BUTTON_GREEN
            circ.fill.solid()
            circ.fill.fore_color.rgb = color
            circ.line.fill.background()
            add_text_in_shape(circ, num, size=11, color=WHITE, bold=True)

            # Title + description
            txBox = slide.shapes.add_textbox(
                Inches(x + 0.5), Inches(y - 0.04), Inches(5.0), Inches(0.65),
            )
            tf = txBox.text_frame
            tf.word_wrap = True
            set_run(tf.paragraphs[0], title, size=13, bold=True, color=DARK_BLUE)
            p2 = tf.add_paragraph()
            p2.space_before = Pt(1)
            set_run(p2, desc, size=10, color=MEDIUM_GRAY)


def slide_23_live_demo(prs):
    """LIVE DEMO slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_dark_bg(slide)

    # Icon
    slide.shapes.add_picture(ICON_PNG, Inches(5.5), Inches(1.2), Inches(2.3))

    # LIVE DEMO text
    txBox = slide.shapes.add_textbox(Inches(2), Inches(3.5), Inches(9), Inches(1.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p, "LIVE DEMO", size=54, bold=True, color=WHITE)

    # Duration
    txBox2 = slide.shapes.add_textbox(Inches(3), Inches(5.2), Inches(7), Inches(0.8))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    set_run(p2, "30 Minutes", size=24, color=LIGHT_BLUE)

    # Accent line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(5.0), Inches(5.0), Inches(3.3), Inches(0.04),
    )
    line.fill.solid()
    line.fill.fore_color.rgb = PRIMARY_BLUE
    line.line.fill.background()


def slide_24_what_you_saw(prs):
    """What You Just Saw slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bullets = [
        "Real-time monitoring \u2014 live CPU, RAM, disk, network metrics via WebSocket",
        "Cross-platform agents \u2014 same management experience on Linux, macOS, Windows, *BSD",
        "One-click operations \u2014 package installs, user management, settings from the browser",
        "Pro+ intelligence layer \u2014 AI health analysis, CIS/STIG compliance, CVE scanning",
        "Enterprise-grade security \u2014 mTLS, tamper-evident audit logs, encrypted secrets",
        "Internationalized UI \u2014 seamless language switching across 14 languages",
    ]
    add_bullet_slide(slide, "What You Just Saw", bullets)


def slide_25_roadmap_overview(prs):
    """Roadmap Overview slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Roadmap Overview")
    add_bottom_bar(slide)
    add_footer_text(slide)

    phases = [
        ("1", "Stabilization", "Feb 2026", True),
        ("2", "Phase 2 Features", "Feb 2026", True),
        ("3", "AV + Firewall", "Apr 2026", False),
        ("4", "Stabilization", "May 2026", False),
        ("5", "Automation + Fleet", "May-Jun 2026", False),
        ("6", "Stabilization", "Jun 2026", False),
        ("7", "Stab. RC1", "Jun 2026", False),
        ("8", "Foundation v2", "Jul 2026", False),
        ("9", "Stab. RC2", "Aug 2026", False),
        ("10", "Virt + Obs + MFA", "Dec 2026", False),
        ("11", "Air-Gapped", "Jan 2027", False),
        ("12", "Enterprise GA", "Feb 2027", False),
    ]

    for i, (num, desc, date, done) in enumerate(phases):
        col = i % 6
        row = i // 6
        x = 0.6 + col * 2.05
        y = 1.7 + row * 2.7

        color = GREEN if done else PRIMARY_BLUE
        box = add_accent_rect(slide, x, y, 1.85, 2.0, color)
        status = "\u2713 Done" if done else date
        add_multiline_in_shape(box, [
            f"Phase {num}",
            "",
            desc,
            "",
            status,
        ], size=11, color=WHITE, bold=False, alignment=PP_ALIGN.CENTER)

    # Target label
    txBox = slide.shapes.add_textbox(Inches(3.0), Inches(6.5), Inches(7), Inches(0.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p, "Target: v3.0.0.0 Enterprise GA \u2014 Q1 2027", size=18, bold=True, color=DARK_BLUE)


def slide_26_futures_near(prs):
    """Futures: Near-Term slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    headers = ["Phase", "Description", "Estimate", "Target"]
    rows = [
        ("3", "AV Management + Firewall Orchestration", "~59 days (padded)", "Apr 2026"),
        ("4", "Stabilization", "~13 days", "May 2026"),
        ("5", "Automation + Fleet Management", "~16 days", "May-Jun 2026"),
    ]
    add_table_slide(slide, "Futures: Near-Term (Phases 3\u20135)", headers, rows,
                    col_widths=[1.5, 5.0, 2.5, 2.0])


def slide_27_futures_mid(prs):
    """Futures: Mid-Term slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    headers = ["Phase", "Description", "Estimate", "Target"]
    rows = [
        ("6", "Stabilization", "~13 days", "Jun 2026"),
        ("7", "Stabilization RC1", "~13 days", "Jun 2026"),
        ("8", "Foundation Features v2.0.0.0", "~25 days", "Jul 2026"),
        ("9", "Stabilization RC2", "~13 days", "Aug 2026"),
    ]
    add_table_slide(slide, "Futures: Mid-Term (Phases 6\u20139)", headers, rows,
                    col_widths=[1.5, 5.0, 2.5, 2.0])


def slide_28_futures_long(prs):
    """Futures: Long-Term slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    headers = ["Phase", "Description", "Estimate", "Target"]
    rows = [
        ("10", "Virtualization + Observability + MFA", "~130 days", "Dec 2026"),
        ("11", "Air-Gapped Support", "~39 days", "Jan 2027"),
        ("12", "Enterprise GA v3.0.0.0", "~31 days", "Feb 2027"),
    ]
    add_table_slide(slide, "Futures: Long-Term (Phases 10\u201312)", headers, rows,
                    col_widths=[1.5, 5.0, 2.5, 2.0])


def slide_29_takeaways(prs):
    """Key Takeaways slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_light_bg(slide)
    add_top_bar(slide)
    add_title_textbox(slide, "Key Takeaways")
    add_bottom_bar(slide)
    add_footer_text(slide)

    takeaways = [
        ("Cross-Platform", "6 operating systems \u2014 Linux, macOS, Windows, FreeBSD, OpenBSD, NetBSD"),
        ("Security-First", "mTLS, JWT rotation, tamper-evident auditing, encrypted secrets, zero inbound agent ports"),
        ("Open Source Core", "AGPLv3 \u2014 transparent, auditable, community-driven foundation"),
        ("Commercial Pro+", "Professional & Enterprise tiers for compliance, AI health, CVE scanning, and more"),
        ("Active Roadmap", "12-phase plan targeting v3.0.0.0 Enterprise GA in Q1 2027"),
    ]

    for i, (title, desc) in enumerate(takeaways):
        y = 1.5 + i * 1.05
        # Accent square
        sq = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.8), Inches(y), Inches(0.15), Inches(0.7),
        )
        sq.fill.solid()
        sq.fill.fore_color.rgb = PRIMARY_BLUE
        sq.line.fill.background()

        # Title
        txBox = slide.shapes.add_textbox(Inches(1.3), Inches(y - 0.05), Inches(10), Inches(0.4))
        tf = txBox.text_frame
        set_run(tf.paragraphs[0], title, size=20, bold=True, color=DARK_BLUE)

        # Description
        txBox2 = slide.shapes.add_textbox(Inches(1.3), Inches(y + 0.35), Inches(10), Inches(0.4))
        tf2 = txBox2.text_frame
        set_run(tf2.paragraphs[0], desc, size=15, color=MEDIUM_GRAY)


def slide_30_thank_you(prs):
    """Thank You slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_dark_bg(slide)

    # Logo
    slide.shapes.add_picture(LOGO_PNG, Inches(4.0), Inches(1.0), Inches(5.3))

    # Thank You
    txBox = slide.shapes.add_textbox(Inches(2), Inches(3.0), Inches(9), Inches(1.0))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p, "Thank You", size=44, bold=True, color=WHITE)

    # URLs
    txBox2 = slide.shapes.add_textbox(Inches(2), Inches(4.3), Inches(9), Inches(2.0))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True

    links = [
        "sysmanage.org",
        "github.com/bceverly/sysmanage",
        "github.com/bceverly/sysmanage-agent",
        "github.com/bceverly/sysmanage-docs",
    ]
    for i, link in enumerate(links):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_before = Pt(6)
        set_run(p, link, size=18, color=LIGHT_BLUE)

    # License
    txBox3 = slide.shapes.add_textbox(Inches(3), Inches(6.0), Inches(7), Inches(0.5))
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    set_run(p3, "Licensed under AGPLv3", size=14, color=MEDIUM_GRAY)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    print("Converting SVG logos to PNG...")
    convert_svgs()

    print("Creating presentation...")
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_builders = [
        slide_01_title,
        slide_02_agenda,
        slide_03_problem,
        slide_04_what_is,
        slide_05_who_bryan,
        slide_06_who_fedor,
        slide_07_growth_strategy,
        slide_08_architecture,
        slide_09_cross_platform,
        slide_10_packaging,
        slide_11_i18n,
        slide_12_oss_features,
        slide_13_oss_monitoring,
        slide_14_proplus_licensing,
        slide_15_proplus_professional,
        slide_16_proplus_enterprise,
        slide_17_ecosystem,
        slide_18_why_security,
        slide_19_security_architecture,
        slide_20_security_devprocess,
        slide_21_sbom,
        slide_22_demo_sequence,
        slide_23_live_demo,
        slide_24_what_you_saw,
        slide_25_roadmap_overview,
        slide_26_futures_near,
        slide_27_futures_mid,
        slide_28_futures_long,
        slide_29_takeaways,
        slide_30_thank_you,
    ]

    for builder in slide_builders:
        name = builder.__name__
        print(f"  Building {name}...")
        builder(prs)

    print(f"Saving to {OUT_FILE}...")
    prs.save(OUT_FILE)
    print(f"Done! {len(prs.slides)} slides created.")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
