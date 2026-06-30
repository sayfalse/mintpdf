from pathlib import Path
from typing import Optional

from ..cover_page import create_cover_page
from ..domain.models import Metadata
from ..metadata import DocumentMetadata
from ..pipeline import (
    DocumentBuilder,
    DocumentLoader,
    LayoutBuilder,
    PDFExporter,
    Renderer,
)
from ..settings import AppSettings
from ..template_manager import TemplateManager
from ..theme_manager import ThemeManager
from ..toc import TOCManager


class ExportService:
    """Service to export documents (currently PDF) using a modular rendering pipeline."""

    def __init__(
        self,
        document_loader: Optional[DocumentLoader] = None,
        document_builder: Optional[DocumentBuilder] = None,
        layout_builder: Optional[LayoutBuilder] = None,
        renderer: Optional[Renderer] = None,
        exporter: Optional[PDFExporter] = None,
    ):
        self.document_loader = document_loader or DocumentLoader()
        self.document_builder = document_builder or DocumentBuilder()
        self.layout_builder = layout_builder or LayoutBuilder()
        self.renderer = renderer or Renderer()
        self.exporter = exporter or PDFExporter()

    def export_to_pdf(
        self,
        text: str,
        output_path: Path,
        metadata: DocumentMetadata,
        settings: AppSettings,
        has_cover: bool = True,
    ) -> bool:
        # Convert Pydantic DocumentMetadata to Domain Metadata
        domain_meta = Metadata(
            title=metadata.title,
            subtitle=metadata.subtitle,
            author=metadata.author,
            organization=metadata.organization,
            date=metadata.date,
            version=metadata.version,
            description=metadata.description,
        )

        # 1. Parse text -> Document domain model
        document = self.document_builder.build(text, domain_meta)

        # Retrieve the configured theme and template
        theme = ThemeManager.get_theme(settings.theme)
        template = TemplateManager.get_template(settings.default_template)

        # 2. Build Layout -> Page domain model
        page_settings = self.layout_builder.build_layout(settings, template)
        document.page_settings = page_settings

        # Prepare flowables list
        story = []

        # 3a. Prepend Cover Page if requested
        if has_cover:
            cover_flowables = create_cover_page(metadata, theme)
            story.extend(cover_flowables)

        # 3b. Extract Headings and compile Table of Contents
        headings = TOCManager.extract_headings(text)
        if settings.auto_toc and headings:
            toc_flowables = TOCManager.generate_toc_flowables(headings, theme)
            story.extend(toc_flowables)

        # 3c. Render body -> flowables list
        body_flowables = self.renderer.render(
            document,
            theme,
            template,
            font_name=settings.default_font.value,
        )
        story.extend(body_flowables)

        # 4. Check for exporter plugin
        fmt = output_path.suffix.lower().lstrip(".")
        from ..plugins.manager import PluginManager

        pm = PluginManager()
        pm.discover_and_load()
        if fmt in pm.exporters:
            return pm.exporters[fmt].export(
                story,
                output_path,
                document,
                settings,
                theme,
                has_cover=has_cover,
            )

        # Default PDF Exporter
        return self.exporter.export(
            story,
            output_path,
            document,
            settings,
            theme,
            has_cover=has_cover,
        )
