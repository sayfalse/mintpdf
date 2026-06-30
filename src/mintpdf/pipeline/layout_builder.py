from ..domain.models import Page, Template
from ..settings import AppSettings


class LayoutBuilder:
    """Stage 3: Layout Builder. Computes layout configuration and returns a domain Page model."""

    def build_layout(self, settings: AppSettings, template: Template) -> Page:
        margins = template.margins or {}
        return Page(
            size=settings.page_size.value,
            margin_top=margins.get("top", 54.0),
            margin_bottom=margins.get("bottom", 54.0),
            margin_left=margins.get("left", 54.0),
            margin_right=margins.get("right", 54.0),
            header_text=None,
            footer_text=None,
        )
