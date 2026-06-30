from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List

from ..domain.models import Document, Theme
from ..settings import AppSettings


class BaseLoader(ABC):
    """Abstract base class for document loader plugins."""

    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        Return list of supported file extensions (e.g. ['.rst', '.html']).
        Should be lowercase and include the leading dot.
        """
        pass

    @abstractmethod
    def load(self, path: Path) -> str:
        """Load file contents and return raw string (e.g. converted to markdown)."""
        pass


class BaseExporter(ABC):
    """Abstract base class for custom document exporter plugins."""

    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        Return list of supported export formats (e.g. ['html', 'json']).
        Should be lowercase.
        """
        pass

    @abstractmethod
    def export(
        self,
        flowables: List[Any],
        output_path: Path,
        document: Document,
        settings: AppSettings,
        theme: Theme,
        has_cover: bool = True,
    ) -> bool:
        """Export flowables and document models to the target path."""
        pass
