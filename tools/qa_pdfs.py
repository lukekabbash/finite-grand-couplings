#!/usr/bin/env python3
"""Structural checks that complement, but do not replace, visual page inspection."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDFS = (
    ROOT / "paper" / "grand-coupling-counterexample.pdf",
    ROOT / "audit" / "internal-verification.pdf",
)


def check_pdf(path: Path):
    if not path.is_file() or path.stat().st_size < 10_000:
        raise AssertionError(f"missing or implausibly small PDF: {path}")
    reader = PdfReader(path)
    if not reader.pages:
        raise AssertionError(f"PDF has no pages: {path}")

    texts = []
    for page_number, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - 612) > 0.5 or abs(height - 792) > 0.5:
            raise AssertionError(
                f"page {page_number} is not US Letter in {path.name}: {width}x{height}"
            )
        text = page.extract_text() or ""
        if len(text.strip()) < 20:
            raise AssertionError(f"blank or nearly blank page {page_number} in {path.name}")
        if "\ufffd" in text or "■" in text:
            raise AssertionError(f"replacement glyph on page {page_number} in {path.name}")
        texts.append(text)

    joined = "\n".join(texts)
    required = (
        "Open Problem 3.11",
        "computer-assisted",
        "independent peer review",
    )
    for phrase in required:
        if phrase not in joined:
            raise AssertionError(f"missing expected phrase {phrase!r} in {path.name}")
    print(f"{path.name}: PASS ({len(reader.pages)} pages, {path.stat().st_size} bytes)")


def main():
    for path in PDFS:
        check_pdf(path)


if __name__ == "__main__":
    main()

