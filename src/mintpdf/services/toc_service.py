from typing import Any, List, Tuple

from ..theme_manager import Theme
from ..toc import TOCManager


class TOCService:
    """Service to generate table of contents flowables."""

    def extract_headings(self, text: str) -> List[Tuple[int, str]]:
        return TOCManager.extract_headings(text)

    def generate_toc_flowables(self, headings: List[Tuple[int, str]], theme: Theme) -> List[Any]:
        return TOCManager.generate_toc_flowables(headings, theme)
