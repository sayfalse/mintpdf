"""
PDF Engine module for Mint PDF.
Handles ReportLab document generation, custom NumberedCanvas for headers/footers,
metadata writing, and document outline bookmarks.
"""

from pathlib import Path
from typing import Any, Optional

from reportlab.lib.colors import HexColor  # type: ignore
from reportlab.lib.pagesizes import A4, legal, letter  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
from reportlab.platypus import (  # type: ignore
    Flowable,
    Paragraph,
    SimpleDocTemplate,
)

from .cover_page import create_cover_page
from .font_manager import FontManager
from .formatter import format_text_to_flowables
from .logger import logger
from .metadata import DocumentMetadata
from .settings import AppSettings
from .template_manager import TemplateManager
from .theme_manager import ThemeManager
from .toc import TOCManager


class BookmarkFlowable(Flowable):
    """
    A ReportLab Flowable that inserts a PDF outline bookmark
    at its layout position on the page.
    """

    def __init__(self, title: str, level: int = 0):
        super().__init__()
        self.title = title
        self.level = level

    def draw(self) -> None:
        # Create a unique key for the bookmark anchor
        key = f"bm_{hash(self.title) & 0xffffffff}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(self.title, key, level=self.level, closed=False)

    def __repr__(self) -> str:
        return f"BookmarkFlowable('{self.title}', level={self.level})"


class NumberedCanvas(canvas.Canvas):
    """
    A two-pass canvas that dynamically calculates the total page count
    and renders styled running headers, footers, and page numbers.
    """

    theme: Optional[Any] = None
    settings: Optional[AppSettings] = None
    metadata: Optional[DocumentMetadata] = None
    has_cover: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        # Save page state for the second rendering pass
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int) -> None:
        """Draws headers, footers, and page numbers on the page canvas."""
        # Ensure we have active configuration
        if not self.settings or not self.theme:
            return

        # Inject native PDF properties on the first page
        if self._pageNumber == 1 and self.metadata:
            self.setTitle(self.metadata.title)
            self.setAuthor(self.metadata.author or "")
            self.setSubject(self.metadata.description or "")
            self.setCreator("Mint PDF")

        # Skip decorations on the cover page (Page 1) if cover page is enabled
        if self.has_cover and self._pageNumber == 1:
            return

        # Font configuration
        font_family = FontManager.get_safe_font_name(self.settings.default_font)

        # Colors
        c_text_muted = HexColor("#718096")

        # Page dimensions
        width, height = self._pagesize
        left_m = self.settings.margins.left
        right_m = self.settings.margins.right
        top_m = self.settings.margins.top
        bottom_m = self.settings.margins.bottom

        # Draw Header
        self.saveState()
        self.setFont(font_family, 8.5)
        self.setFillColor(c_text_muted)

        # Header text
        doc_title = self.metadata.title if self.metadata else "Mint PDF Document"
        self.drawString(left_m, height - top_m + 15, doc_title)

        # Header line
        self.setStrokeColor(HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(left_m, height - top_m + 8, width - right_m, height - top_m + 8)

        # Draw Footer
        # Footer line
        self.line(left_m, bottom_m - 8, width - right_m, bottom_m - 8)

        # Footer text (left aligned)
        footer_left = "Mint PDF Generator"
        self.drawString(left_m, bottom_m - 20, footer_left)

        # Page numbers (right aligned)
        if self.settings.auto_page_numbers:
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(width - right_m, bottom_m - 20, page_text)

        self.restoreState()


def generate_pdf(
    text: str,
    output_path: Path,
    metadata: DocumentMetadata,
    settings: AppSettings,
    has_cover: bool = True,
) -> bool:
    """
    Compiles input text, TOC, and cover pages into a styled PDF document using ReportLab.

    Args:
        text: Raw document text to convert.
        output_path: The file path to save the generated PDF.
        metadata: The DocumentMetadata instance.
        settings: The AppSettings instance.
        has_cover: If True, prepend a cover page.

    Returns:
        True if PDF generated successfully, False otherwise.
    """
    try:
        logger.info(f"Starting ReportLab PDF compilation for: {output_path}")

        # Parse Page Size
        page_size = letter
        sz_upper = settings.page_size.upper()
        if sz_upper == "A4":
            page_size = A4
        elif sz_upper == "LEGAL":
            page_size = legal

        # Get target Theme
        theme = ThemeManager.get_theme(settings.theme)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=page_size,
            leftMargin=settings.margins.left,
            rightMargin=settings.margins.right,
            topMargin=settings.margins.top,
            bottomMargin=settings.margins.bottom,
        )

        # Initialize NumberedCanvas static variables
        NumberedCanvas.theme = theme
        NumberedCanvas.settings = settings
        NumberedCanvas.metadata = metadata
        NumberedCanvas.has_cover = has_cover

        story = []

        # 1. Prepend Cover Page if requested
        if has_cover:
            logger.info("Building cover page flowables...")
            cover_flowables = create_cover_page(metadata, theme)
            story.extend(cover_flowables)

        # 2. Extract Headings and compile Table of Contents
        headings = TOCManager.extract_headings(text)
        if settings.auto_toc and headings:
            logger.info(f"Building Table of Contents for {len(headings)} headings...")
            toc_flowables = TOCManager.generate_toc_flowables(headings, theme)
            story.extend(toc_flowables)

        # 3. Format main body text to flowables with Bookmark annotations
        logger.info("Formatting document body...")
        template = TemplateManager.get_template(settings.default_template)
        body_flowables = format_text_to_flowables(text, theme, template, settings.default_font)

        # We inject BookmarkFlowables immediately before headings
        final_body = []
        for flowable in body_flowables:
            if isinstance(flowable, Paragraph) and flowable.style.name in [
                "MintH1",
                "MintH2",
                "MintH3",
            ]:
                level = 0
                if flowable.style.name == "MintH2":
                    level = 1
                elif flowable.style.name == "MintH3":
                    level = 2
                # Prepend the outline bookmark
                final_body.append(BookmarkFlowable(flowable.text, level))
            final_body.append(flowable)

        story.extend(final_body)

        # 4. Compile document using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)

        # 5. Inject PDF standard document metadata properties after building
        # ReportLab supports setting metadata via pdfgen.canvas or post-processors,
        # but the cleanest way is standard file info fields.
        logger.info("PDF document built successfully.")
        return True

    except Exception as e:
        logger.error(f"Error compiling PDF at {output_path}: {e}", exc_info=True)
        return False
