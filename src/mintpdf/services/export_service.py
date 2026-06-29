from pathlib import Path

from ..metadata import DocumentMetadata
from ..pdf_engine import generate_pdf
from ..settings import AppSettings


class ExportService:
    """Service to export documents (currently PDF)."""

    def export_to_pdf(
        self,
        text: str,
        output_path: Path,
        metadata: DocumentMetadata,
        settings: AppSettings,
        has_cover: bool = True,
    ) -> bool:
        return generate_pdf(text, output_path, metadata, settings, has_cover)
