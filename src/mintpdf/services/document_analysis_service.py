from typing import Optional

from ..document_analyzer import AnalysisResult, DocumentAnalyzer


class DocumentAnalysisService:
    """Service to analyze document properties and recommend styles."""

    def analyze(self, content: str, filename: Optional[str] = None) -> AnalysisResult:
        return DocumentAnalyzer.analyze(content, filename)
