from typing import List

from ..theme_manager import Theme, ThemeManager


class ThemeService:
    """Service to manage styling themes."""

    def get_theme(self, name: str) -> Theme:
        return ThemeManager.get_theme(name)

    def get_all_theme_names(self) -> List[str]:
        return ThemeManager.get_all_theme_names()

    def load_custom_themes(self) -> None:
        ThemeManager.load_custom_themes()
