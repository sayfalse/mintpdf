from pathlib import Path

from ..file_manager import read_document
from ..plugins.manager import PluginManager


class DocumentLoader:
    """Stage 1: Document Loader. Loads raw content from files."""

    def load(self, path: Path) -> str:
        # Check if there is a loader plugin registered for this extension
        ext = path.suffix.lower()
        pm = PluginManager()
        pm.discover_and_load()  # Ensure plugins are loaded
        if ext in pm.loaders:
            return pm.loaders[ext].load(path)
        return read_document(path)
