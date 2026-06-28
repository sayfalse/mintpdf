"""
Table of Contents (TOC) generator module for Mint PDF.
Scans structural elements and builds a clean, dot-leader TOC section.
"""

import re
from typing import Any, List, Tuple

from reportlab.lib.colors import HexColor  # type: ignore
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore
from reportlab.platypus import PageBreak, Paragraph, Spacer  # type: ignore

from .theme_manager import Theme


class TOCManager:
    """Manages TOC parsing and compilation of the Table of Contents section."""

    @staticmethod
    def extract_headings(text: str) -> List[Tuple[int, str]]:
        """
        Scans a document text for Markdown headers and extracts them for the TOC.

        Args:
            text: Raw input document text.

        Returns:
            A list of tuples (heading_level, heading_text).
        """
        headings = []
        in_code_block = False

        for line in text.splitlines():
            line_stripped = line.strip()

            # Skip code blocks
            if line_stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Detect Heading 1, 2, 3
            if line_stripped.startswith("# "):
                headings.append((1, line_stripped[2:].strip()))
            elif line_stripped.startswith("## "):
                headings.append((2, line_stripped[3:].strip()))
            elif line_stripped.startswith("### "):
                headings.append((3, line_stripped[4:].strip()))

        return headings

    @staticmethod
    def generate_toc_flowables(headings: List[Tuple[int, str]], theme: Theme) -> List[Any]:
        """
        Creates a visual Table of Contents with dot leaders connecting headings and mock page numbers.

        Args:
            headings: List of tuples (level, heading_text).
            theme: The visual Theme.

        Returns:
            List of ReportLab flowable elements.
        """
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TOCTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            textColor=HexColor(theme.primary),
            spaceAfter=20,
        )

        item_style = ParagraphStyle(
            "TOCItem",
            parent=styles["Normal"],
            fontName="Helvetica",
            textColor=HexColor(theme.text),
            spaceAfter=6,
        )

        story.append(Paragraph("Table of Contents", title_style))
        story.append(Spacer(1, 10))

        if not headings:
            story.append(Paragraph("<i>No headings detected to generate TOC.</i>", item_style))
            story.append(Spacer(1, 20))
            story.append(PageBreak())
            return story

        # Generate entries with dot leaders
        # Example format: Introduction .................................................... 1
        for level, heading_text in headings:
            # Format text (strip inline markdown markers)
            clean_text = re.sub(r"[\*\_`]", "", heading_text)

            indent = "&nbsp;" * ((level - 1) * 4)
            # Dot leader calculation: approximate width in monospaced/dot-character sequence
            dots_count = max(5, 75 - len(clean_text) - ((level - 1) * 4))
            dots = "." * dots_count

            # Simple page numbers for display
            mock_page = 2 + (level * 2)

            entry_html = f"{indent}{clean_text} {dots} {mock_page}"
            story.append(Paragraph(entry_html, item_style))

        story.append(PageBreak())
        return story
