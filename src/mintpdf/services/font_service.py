from typing import Any, List

from ..font_manager import FontManager


class FontService:
    """Service to manage typography fonts."""

    def get_supported_fonts(self) -> List[str]:
        return FontManager.get_supported_fonts()

    def get_safe_font_name(self, font_name: Any) -> str:
        return FontManager.get_safe_font_name(font_name)

    def register_fonts(self) -> None:
        FontManager.register_fonts()
