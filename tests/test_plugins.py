from pathlib import Path
from typing import Any, List

from mintpdf.domain.models import Document, Theme
from mintpdf.metadata import DocumentMetadata
from mintpdf.pipeline import DocumentLoader
from mintpdf.plugins import BaseExporter, BaseLoader, PluginManager
from mintpdf.services import ExportService
from mintpdf.settings import AppSettings


class MockLoader(BaseLoader):
    def supported_extensions(self) -> List[str]:
        return [".mock"]

    def load(self, path: Path) -> str:
        return f"Mock Loaded: {path.name}"


class MockExporter(BaseExporter):
    def supported_formats(self) -> List[str]:
        return ["mock"]

    def export(
        self,
        flowables: List[Any],
        output_path: Path,
        document: Document,
        settings: AppSettings,
        theme: Theme,
        has_cover: bool = True,
    ) -> bool:
        output_path.write_text("Mock Export Success", encoding="utf-8")
        return True


def test_plugin_registration(tmp_path):
    # Set up temporary plugins folder
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    # Write a test plugin python file
    plugin_code = """
from typing import List, Any
from pathlib import Path
from mintpdf.plugins import BaseLoader, BaseExporter
from mintpdf.domain.models import Document, Theme
from mintpdf.settings import AppSettings

class PluginCustomLoader(BaseLoader):
    def supported_extensions(self) -> List[str]:
        return [".custom"]
    def load(self, path: Path) -> str:
        return "Custom Loader Success"

class PluginCustomExporter(BaseExporter):
    def supported_formats(self) -> List[str]:
        return ["custom"]
    def export(self, flowables: List[Any], output_path: Path, document: Document, settings: AppSettings, theme: Theme, has_cover: bool = True) -> bool:
        output_path.write_text("Custom Exporter Success", encoding="utf-8")
        return True

# Define a custom theme to register
from mintpdf.domain.models import Theme as DomainTheme
THEMES = [
    DomainTheme(name="PluginTheme", primary="#FF0000", secondary="#00FF00", accent="#0000FF", text="#000000")
]
"""
    (plugins_dir / "my_plugin.py").write_text(plugin_code, encoding="utf-8")

    # Initialize PluginManager and load
    PluginManager._instance = None
    PluginManager._initialized = False
    pm = PluginManager(plugins_dir=str(plugins_dir))
    pm.loaders.clear()
    pm.exporters.clear()
    pm.discover_and_load()

    assert ".custom" in pm.loaders
    assert "custom" in pm.exporters

    # Verify loader integration
    loader = DocumentLoader()
    test_file = tmp_path / "doc.custom"
    test_file.write_text("data", encoding="utf-8")
    content = loader.load(test_file)
    assert content == "Custom Loader Success"

    # Verify exporter integration
    service = ExportService()
    out_file = tmp_path / "doc.custom"
    meta = DocumentMetadata(title="Test")
    settings = AppSettings()
    success = service.export_to_pdf("text", out_file, meta, settings, has_cover=False)
    assert success is True
    assert out_file.read_text(encoding="utf-8") == "Custom Exporter Success"

    # Restore default PluginManager configuration for subsequent runs
    PluginManager._instance = None
    PluginManager._initialized = False
    PluginManager(plugins_dir="plugins")
    PluginManager(plugins_dir="plugins")
