from pathlib import Path

from ..file_manager import read_document


class DocumentLoader:
    """Stage 1: Document Loader. Loads raw content from files."""

    def load(self, path: Path) -> str:
        return read_document(path)
