#!/usr/bin/env python3
"""Render INTERNAL_VERIFICATION.md as a restrained academic PDF."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import NextPageTemplate, Paragraph, Spacer


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

from academic_pdf import (  # noqa: E402
    AUTHOR,
    BODY,
    BODY_SMALL,
    BULLET,
    DATE,
    H1 as H1_STYLE,
    H2 as H2_STYLE,
    INK,
    PROOF,
    SUBTITLE,
    TITLE,
    Rule,
    booktabs,
    bullet,
    code_block,
    h1,
    h2,
    make_document,
    p,
)


SOURCE = Path(__file__).resolve().with_name("INTERNAL_VERIFICATION.md")
OUTPUT = Path(__file__).resolve().with_name("internal-verification.pdf")
TITLE_TEXT = "Internal Verification Report"
SHORT_TITLE = "Internal verification report"
DATE_TEXT = "20 July 2026"

# The verification report is denser than the article. A slightly tighter
# measure keeps the audit continuous without sacrificing a readable type size.
BODY.fontSize = 10.2
BODY.leading = 13.5
BODY.spaceAfter = 5.9
BODY_SMALL.fontSize = 8.95
BODY_SMALL.leading = 11.9
PROOF.fontSize = 10.2
PROOF.leading = 13.5
BULLET.fontSize = 10.2
BULLET.leading = 13.5
H1_STYLE.spaceBefore = 10.5
H2_STYLE.spaceBefore = 7


def inline_markdown(text: str) -> str:
    code_spans: list[str] = []

    def save_code(match):
        code_spans.append(html.escape(match.group(1)))
        return f"@@CODE{len(code_spans) - 1}@@"

    text = re.sub(r"`([^`]+)`", save_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r"<link href='\2' color='#294C69'>\1</link>",
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for index, code in enumerate(code_spans):
        text = text.replace(
            f"@@CODE{index}@@", f"<font name='Courier' size='8.2'>{code}</font>"
        )
    return text


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_widths(rows: list[list[str]], width: float) -> list[float]:
    columns = len(rows[0])
    weights = []
    for column in range(columns):
        longest = max(len(re.sub(r"[`*_]", "", row[column])) for row in rows)
        weights.append(max(9, min(34, longest)))
    total = sum(weights)
    return [width * weight / total for weight in weights]


def render_markdown(source: str, width: float):
    lines = source.splitlines()
    first_section = next(index for index, line in enumerate(lines) if line.startswith("## "))
    lines = lines[first_section:]
    story = []
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("## "):
            story.append(h1(inline_markdown(stripped[3:])))
            index += 1
            continue

        if stripped.startswith("### "):
            story.append(h2(inline_markdown(stripped[4:])))
            index += 1
            continue

        if stripped.startswith("```"):
            code = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError("unterminated code fence")
            story.append(code_block(code, width))
            index += 1
            continue

        if stripped.startswith("|"):
            raw_rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                raw_rows.append(lines[index].strip())
                index += 1
            rows = [
                [inline_markdown(cell.strip()) for cell in row.strip("|").split("|")]
                for row in raw_rows
                if not is_table_separator(row)
            ]
            if not rows or any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("malformed Markdown table")
            story.append(booktabs(rows, table_widths(rows, width), font_size=7.75))
            story.append(Spacer(1, 5))
            continue

        if stripped.startswith("- "):
            while index < len(lines) and lines[index].strip().startswith("- "):
                story.append(bullet(inline_markdown(lines[index].strip()[2:])))
                index += 1
            continue

        if stripped.startswith("> "):
            quote = []
            while index < len(lines) and lines[index].strip().startswith("> "):
                quote.append(lines[index].strip()[2:])
                index += 1
            story.append(Paragraph(inline_markdown(" ".join(quote)), PROOF))
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index].strip()
            if not candidate:
                break
            if (
                candidate.startswith("## ")
                or candidate.startswith("### ")
                or candidate.startswith("```")
                or candidate.startswith("|")
                or candidate.startswith("- ")
                or candidate.startswith("> ")
            ):
                break
            paragraph.append(candidate)
            index += 1
        story.append(p(inline_markdown(" ".join(paragraph)), BODY))

    return story


def build():
    doc, width = make_document(
        OUTPUT,
        title=TITLE_TEXT,
        author="Anonymous",
        subject="Internal adversarial verification of the grand-coupling counterexample",
        short_title=SHORT_TITLE,
    )
    story = [
        Spacer(1, 15),
        p(TITLE_TEXT, TITLE),
        p(
            "Grand-coupling counterexample and computer-assisted state-minimality theorem",
            SUBTITLE,
        ),
        p("Anonymous research draft", AUTHOR),
        p(DATE_TEXT, DATE),
        Rule(color=INK, thickness=0.75, space_after=11),
        p(
            "<b>Nature of review.</b> Internal adversarial verification. This report records what was checked, what depends on computation, and what remains outside the evidence. It is not independent peer review.",
            BODY_SMALL,
        ),
        NextPageTemplate("body"),
    ]
    story.extend(render_markdown(SOURCE.read_text(encoding="utf-8"), width))
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
