#!/usr/bin/env python3
"""Shared, dependency-light typography for the two release PDFs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


INK = colors.HexColor("#171717")
MUTED = colors.HexColor("#565B60")
ACCENT = colors.HexColor("#294C69")
HAIRLINE = colors.HexColor("#AEB5BB")
LIGHT = colors.HexColor("#E9EDF0")
WHITE = colors.white

SERIF = "Times-Roman"
SERIF_BOLD = "Times-Bold"
SERIF_ITALIC = "Times-Italic"
SANS = "Helvetica"
SANS_BOLD = "Helvetica-Bold"
MONO = "Courier"


class AcademicDocTemplate(BaseDocTemplate):
    """Adds PDF outline entries for marked paragraph headings."""

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        level = getattr(flowable, "outline_level", None)
        if level is None:
            return
        key = f"heading-{self.page}-{id(flowable)}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(
            flowable.getPlainText(), key, level=level, closed=False
        )


class Heading(Paragraph):
    def __init__(self, text: str, style: ParagraphStyle, level: int):
        super().__init__(text, style)
        self.outline_level = level


class Rule(Flowable):
    def __init__(
        self,
        *,
        color=HAIRLINE,
        thickness: float = 0.55,
        space_before: float = 3,
        space_after: float = 7,
    ):
        super().__init__()
        self.color = color
        self.thickness = thickness
        self.space_before = space_before
        self.space_after = space_after
        self.height = space_before + thickness + space_after

    def wrap(self, avail_width, avail_height):
        self._avail_width = avail_width
        return avail_width, self.height

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space_after, self._avail_width, self.space_after)


BODY = ParagraphStyle(
    "Body",
    fontName=SERIF,
    fontSize=10.35,
    leading=13.85,
    textColor=INK,
    alignment=TA_LEFT,
    spaceAfter=6.4,
    allowWidows=0,
    allowOrphans=0,
)
BODY_SMALL = ParagraphStyle(
    "BodySmall",
    parent=BODY,
    fontSize=9.05,
    leading=12.1,
    spaceAfter=5.2,
)
ABSTRACT = ParagraphStyle(
    "Abstract",
    parent=BODY,
    fontSize=9.65,
    leading=13.2,
    leftIndent=0.22 * inch,
    rightIndent=0.22 * inch,
    spaceAfter=7,
)
TITLE = ParagraphStyle(
    "Title",
    fontName=SERIF_BOLD,
    fontSize=23.5,
    leading=26.5,
    textColor=INK,
    alignment=TA_CENTER,
    spaceAfter=10,
)
SUBTITLE = ParagraphStyle(
    "Subtitle",
    fontName=SERIF_ITALIC,
    fontSize=11.2,
    leading=14.2,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceAfter=9,
)
AUTHOR = ParagraphStyle(
    "Author",
    fontName=SERIF,
    fontSize=10.2,
    leading=13,
    textColor=INK,
    alignment=TA_CENTER,
    spaceAfter=2,
)
DATE = ParagraphStyle(
    "Date",
    parent=AUTHOR,
    fontSize=9.2,
    textColor=MUTED,
    spaceAfter=13,
)
H1 = ParagraphStyle(
    "H1",
    fontName=SERIF_BOLD,
    fontSize=13.5,
    leading=16.4,
    textColor=INK,
    spaceBefore=12,
    spaceAfter=6,
    keepWithNext=True,
)
H2 = ParagraphStyle(
    "H2",
    fontName=SERIF_ITALIC,
    fontSize=11.2,
    leading=14,
    textColor=INK,
    spaceBefore=8,
    spaceAfter=4.5,
    keepWithNext=True,
)
THEOREM = ParagraphStyle(
    "Theorem",
    parent=BODY,
    fontName=SERIF_ITALIC,
    leftIndent=0.18 * inch,
    rightIndent=0.18 * inch,
    spaceBefore=5,
    spaceAfter=6,
)
THEOREM_LABEL = ParagraphStyle(
    "TheoremLabel",
    parent=THEOREM,
    fontName=SERIF_BOLD,
    keepWithNext=True,
    spaceAfter=3,
)
PROOF = ParagraphStyle(
    "Proof",
    parent=BODY,
    leftIndent=0.18 * inch,
    rightIndent=0.18 * inch,
)
EQUATION = ParagraphStyle(
    "Equation",
    parent=BODY,
    fontSize=10.7,
    leading=15,
    alignment=TA_CENTER,
    leftIndent=0.3 * inch,
    rightIndent=0.3 * inch,
    spaceBefore=3,
    spaceAfter=7,
)
CAPTION = ParagraphStyle(
    "Caption",
    parent=BODY_SMALL,
    fontSize=8.55,
    leading=11,
    textColor=MUTED,
    spaceBefore=4,
    spaceAfter=8,
)
BULLET = ParagraphStyle(
    "Bullet",
    parent=BODY,
    leftIndent=0.24 * inch,
    firstLineIndent=-0.12 * inch,
    bulletIndent=0.06 * inch,
    spaceAfter=3.5,
)
REFERENCE = ParagraphStyle(
    "Reference",
    parent=BODY_SMALL,
    fontSize=8.55,
    leading=11.1,
    leftIndent=0.25 * inch,
    firstLineIndent=-0.25 * inch,
    spaceAfter=3.2,
)
CODE = ParagraphStyle(
    "Code",
    fontName=MONO,
    fontSize=7.65,
    leading=9.8,
    textColor=INK,
    spaceAfter=0,
)


def p(text: str, style: ParagraphStyle = BODY) -> Paragraph:
    return Paragraph(text, style)


def h1(text: str) -> Heading:
    return Heading(text, H1, 0)


def h2(text: str) -> Heading:
    return Heading(text, H2, 1)


def bullet(text: str) -> Paragraph:
    return Paragraph(f"•&nbsp; {text}", BULLET)


def equation(text: str) -> Paragraph:
    return Paragraph(text, EQUATION)


def theorem(label: str, statement: Sequence[str]) -> KeepTogether:
    items = [Paragraph(label, THEOREM_LABEL)]
    items.extend(Paragraph(text, THEOREM) for text in statement)
    return KeepTogether(items)


def proof_start(text: str) -> Paragraph:
    return Paragraph(f"<i>Proof.</i> {text}", PROOF)


def booktabs(
    rows: Sequence[Sequence[str]],
    widths: Sequence[float],
    *,
    font_size: float = 8.25,
    repeat_rows: int = 1,
) -> Table:
    converted = []
    for row_index, row in enumerate(rows):
        style = ParagraphStyle(
            f"table-{id(rows)}-{row_index}",
            parent=BODY_SMALL,
            fontName=SANS_BOLD if row_index < repeat_rows else SERIF,
            fontSize=font_size,
            leading=font_size + 2.5,
            textColor=INK,
            spaceAfter=0,
        )
        converted.append([Paragraph(str(cell), style) for cell in row])
    table = Table(converted, colWidths=widths, repeatRows=repeat_rows, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK),
        ("LINEBELOW", (0, repeat_rows - 1), (-1, repeat_rows - 1), 0.45, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, INK),
    ]
    table.setStyle(TableStyle(commands))
    return table


def code_block(lines: Iterable[str], width: float) -> KeepTogether:
    escaped = []
    for line in lines:
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        escaped.append(Paragraph(safe or "&nbsp;", CODE))
    table = Table([[escaped]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F4")),
                ("LINEABOVE", (0, 0), (-1, 0), 0.45, HAIRLINE),
                ("LINEBELOW", (0, -1), (-1, -1), 0.45, HAIRLINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return KeepTogether([table, Spacer(1, 6)])


def _header(short_title: str):
    def draw(canvas: Canvas, doc):
        canvas.saveState()
        page_width, page_height = LETTER
        canvas.setStrokeColor(HAIRLINE)
        canvas.setLineWidth(0.35)
        canvas.line(doc.leftMargin, page_height - 39, page_width - doc.rightMargin, page_height - 39)
        canvas.setFillColor(MUTED)
        canvas.setFont(SANS, 7)
        canvas.drawString(doc.leftMargin, page_height - 30, short_title.upper())
        canvas.drawRightString(page_width - doc.rightMargin, page_height - 30, str(doc.page))
        canvas.restoreState()

    return draw


def _first_page(canvas: Canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont(SANS, 7)
    canvas.drawCentredString(LETTER[0] / 2, 29, str(doc.page))
    canvas.restoreState()


def make_document(
    output: Path,
    *,
    title: str,
    author: str,
    subject: str,
    short_title: str,
) -> tuple[AcademicDocTemplate, float]:
    output.parent.mkdir(parents=True, exist_ok=True)
    left = right = 1.0 * inch
    top = 0.72 * inch
    bottom = 0.68 * inch
    page_width, page_height = LETTER
    doc = AcademicDocTemplate(
        str(output),
        pagesize=LETTER,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
        bottomMargin=bottom,
        title=title,
        author=author,
        subject=subject,
        creator="ReportLab academic release builder",
        invariant=1,
        pageCompression=1,
    )
    frame = Frame(
        left,
        bottom,
        page_width - left - right,
        page_height - top - bottom,
        id="body",
    )
    doc.addPageTemplates(
        [
            PageTemplate(
                id="first",
                frames=[frame],
                onPage=_first_page,
                autoNextPageTemplate="body",
            ),
            PageTemplate(id="body", frames=[frame], onPage=_header(short_title)),
        ]
    )
    return doc, page_width - left - right
