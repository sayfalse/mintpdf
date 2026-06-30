from pathlib import Path
from typing import Any, List

from reportlab.lib.pagesizes import A4, legal, letter  # type: ignore
from reportlab.platypus import (
    Paragraph as RLParagraph,
)
from reportlab.platypus import (  # type: ignore
    SimpleDocTemplate,
)

from ..domain.models import Document, Theme
from ..logger import logger
from ..pdf_engine import BookmarkFlowable, NumberedCanvas
from ..settings import AppSettings


class PDFExporter:
    """Stage 5: Exporter. Compiles flowables into a PDF using ReportLab."""

    def export(
        self,
        flowables: List[Any],
        output_path: Path,
        document: Document,
        settings: AppSettings,
        theme: Theme,
        has_cover: bool = True,
    ) -> bool:
        try:
            logger.info(f"Starting ReportLab PDF compilation via pipeline exporter: {output_path}")

            # Parse Page Size
            page_size = letter
            sz_upper = settings.page_size.upper()
            if sz_upper == "A4":
                page_size = A4
            elif sz_upper == "LEGAL":
                page_size = legal

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=page_size,
                leftMargin=settings.margins.left,
                rightMargin=settings.margins.right,
                topMargin=settings.margins.top,
                bottomMargin=settings.margins.bottom,
            )

            # Initialize NumberedCanvas static variables
            from ..metadata import DocumentMetadata

            meta = document.metadata
            kwargs = {
                "title": meta.title,
                "subtitle": meta.subtitle,
                "author": meta.author,
                "organization": meta.organization,
                "version": meta.version or "1.0.0",
                "description": meta.description,
            }
            if meta.date is not None:
                kwargs["date"] = meta.date
            doc_metadata = DocumentMetadata(**kwargs)

            NumberedCanvas.theme = theme
            NumberedCanvas.settings = settings
            NumberedCanvas.metadata = doc_metadata
            NumberedCanvas.has_cover = has_cover

            # We inject BookmarkFlowables immediately before headings in flowables
            final_flowables = []
            for flowable in flowables:
                if isinstance(flowable, RLParagraph) and flowable.style.name in [
                    "MintH1",
                    "MintH2",
                    "MintH3",
                ]:
                    level = 0
                    if flowable.style.name == "MintH2":
                        level = 1
                    elif flowable.style.name == "MintH3":
                        level = 2
                    final_flowables.append(BookmarkFlowable(flowable.text, level))
                final_flowables.append(flowable)

            # Build PDF
            doc.build(final_flowables, canvasmaker=NumberedCanvas)
            logger.info("PDF document built successfully via pipeline exporter.")
            from ..event_dispatcher import EventDispatcher

            EventDispatcher().publish("pdf:compiled", output_path=output_path)
            return True
        except Exception as e:
            logger.error(f"Error in pipeline PDF exporter: {e}", exc_info=True)
            return False
