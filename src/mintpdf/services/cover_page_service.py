from typing import Any, List

from ..cover_page import create_cover_page
from ..metadata import DocumentMetadata
from ..theme_manager import Theme


class CoverPageService:
    """Service to compile cover page flowables."""

    def generate_cover_flowables(self, metadata: DocumentMetadata, theme: Theme) -> List[Any]:
        return create_cover_page(metadata, theme)
