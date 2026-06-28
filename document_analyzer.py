"""
Document Analyzer module for Mint PDF.
An offline rule-based parser that detects structural elements in plain text
and recommends document styling templates, themes, fonts, and filenames.
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from logger import logger

class AnalysisResult:
    """Stores the structural statistics and layout recommendations for an analyzed document."""
    def __init__(self):
        self.title: str = "Untitled"
        self.headings_count: int = 0
        self.subheadings_count: int = 0
        self.paragraphs_count: int = 0
        self.lists_count: int = 0
        self.tables_count: int = 0
        self.images_count: int = 0
        self.quotes_count: int = 0
        self.code_blocks_count: int = 0
        self.references_count: int = 0
        self.footnotes_count: int = 0
        self.estimated_pages: int = 1
        
        # Recommendations
        self.recommended_template: str = "Standard"
        self.recommended_theme: str = "Professional"
        self.recommended_font: str = "Helvetica"
        self.recommended_filename: str = "document.pdf"
        self.document_type: str = "Standard Document"

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to a structured dictionary."""
        return {
            "title": self.title,
            "headings_count": self.headings_count,
            "subheadings_count": self.subheadings_count,
            "paragraphs_count": self.paragraphs_count,
            "lists_count": self.lists_count,
            "tables_count": self.tables_count,
            "images_count": self.images_count,
            "quotes_count": self.quotes_count,
            "code_blocks_count": self.code_blocks_count,
            "references_count": self.references_count,
            "footnotes_count": self.footnotes_count,
            "estimated_pages": self.estimated_pages,
            "recommended_template": self.recommended_template,
            "recommended_theme": self.recommended_theme,
            "recommended_font": self.recommended_font,
            "recommended_filename": self.recommended_filename,
            "document_type": self.document_type
        }

class DocumentAnalyzer:
    """Analyzes raw text/markdown to extract structure and propose style settings."""

    @staticmethod
    def slugify(text: str) -> str:
        """Utility to convert text to a clean filename slug."""
        text = text.lower().strip()
        # Remove any markdown styling tags from title before slugifying
        text = re.sub(r"[\*\_`#]", "", text)
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "_", text)
        return text

    @classmethod
    def analyze(cls, text: str, original_filename: Optional[str] = None) -> AnalysisResult:
        """
        Runs rule-based detection on plain text/markdown.
        
        Args:
            text: Raw string content of the document.
            original_filename: The name of the imported file if loaded from disk.
            
        Returns:
            An AnalysisResult object containing counts and styling recommendations.
        """
        result = AnalysisResult()
        
        if not text.strip():
            return result
            
        lines = text.splitlines()
        in_code_block = False
        in_table = False
        
        # Regex patterns
        h1_pattern = re.compile(r"^#\s+(.+)$")
        h2_pattern = re.compile(r"^##\s+(.+)$|^###\s+(.+)$")
        list_pattern = re.compile(r"^(\s*)[-\*\+]\s+(.+)$|^(\s*)\d+\.\s+(.+)$")
        quote_pattern = re.compile(r"^>\s+(.+)$")
        table_pattern = re.compile(r"^\|.+(?:\|.+)*\|$")
        image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
        reference_pattern = re.compile(r"^\[\d+\]\s+(.+)$|^References|^Bibliography", re.IGNORECASE)
        footnote_pattern = re.compile(r"^\[\^\w+\]:?\s+(.+)$")
        
        # Additional tokens count for heuristic matrix
        inline_code_occurrences = 0
        citation_matches = 0
        dialogue_occurrences = 0
        total_words = 0
        
        total_lines = len(lines)
        i = 0
        
        while i < total_lines:
            line = lines[i]
            line_stripped = line.strip()
            
            if not line_stripped:
                i += 1
                continue
                
            total_words += len(line_stripped.split())
            
            # Inline code search
            inline_code_occurrences += len(re.findall(r"`.*?`", line_stripped))
            
            # Academic brackets citations [12] or (Author, 2024)
            citation_matches += len(re.findall(r"\[\d+\]|\([A-Za-z]+,\s*\d{4}\)", line_stripped))
            
            # Dialogue occurrences (creative quotes or em-dash lists)
            if line_stripped.startswith('"') or line_stripped.startswith('“') or line_stripped.startswith('—'):
                dialogue_occurrences += 1
            
            # 1. Code block detection
            if line_stripped.startswith("```"):
                in_code_block = not in_code_block
                if in_code_block:
                    result.code_blocks_count += 1
                i += 1
                continue
                
            if in_code_block:
                i += 1
                continue
                
            # 2. Image detection (within line)
            images_found = image_pattern.findall(line_stripped)
            if images_found:
                result.images_count += len(images_found)
                
            # 3. Table detection
            if table_pattern.match(line_stripped):
                if not in_table:
                    result.tables_count += 1
                    in_table = True
                i += 1
                continue
            else:
                in_table = False

            # 4. Setext Headings check (Underlines of === or ---)
            if i + 1 < total_lines:
                next_line_stripped = lines[i+1].strip()
                if len(next_line_stripped) >= 3:
                    if all(char == "=" for char in next_line_stripped):
                        result.headings_count += 1
                        if result.title == "Untitled":
                            result.title = line_stripped
                        i += 2 # skip heading underline
                        continue
                    elif all(char == "-" for char in next_line_stripped):
                        result.subheadings_count += 1
                        i += 2 # skip subheading underline
                        continue

            # 5. ATX Heading 1 / Title detection
            h1_match = h1_pattern.match(line_stripped)
            if h1_match:
                result.headings_count += 1
                if result.title == "Untitled":
                    result.title = h1_match.group(1).strip()
                i += 1
                continue
                
            # 6. ATX Heading 2/3 / Subheading detection
            h2_match = h2_pattern.match(line_stripped)
            if h2_match:
                result.subheadings_count += 1
                i += 1
                continue

            # 7. List detection
            if list_pattern.match(line_stripped):
                result.lists_count += 1
                i += 1
                continue

            # 8. Quote detection
            if quote_pattern.match(line_stripped):
                result.quotes_count += 1
                i += 1
                continue

            # 9. Footnotes
            if footnote_pattern.match(line_stripped):
                result.footnotes_count += 1
                i += 1
                continue

            # 10. References
            if reference_pattern.match(line_stripped):
                result.references_count += 1
                i += 1
                continue

            # Default paragraph line count
            result.paragraphs_count += 1
            i += 1

        # Adjust paragraph counts (lines aren't exactly paragraphs, so scale it down)
        result.paragraphs_count = max(1, int(result.paragraphs_count / 3))

        # Estimate pages: minimum 1, ~350-400 words per page average
        result.estimated_pages = max(1, int(total_words / 350) + 1)
        if result.headings_count > 10:
            result.estimated_pages += int(result.headings_count / 8)

        # Heuristic Scoring Matrix
        technical_score = (result.code_blocks_count * 5) + (inline_code_occurrences * 2) + (result.lists_count * 0.5)
        academic_score = (result.references_count * 5) + (result.footnotes_count * 5) + (citation_matches * 2)
        creative_score = (result.quotes_count * 4) + (dialogue_occurrences * 0.5)
        datasheet_score = (result.tables_count * 8)
        
        scores = {
            "Technical Documentation": technical_score,
            "Academic Paper": academic_score,
            "Creative Novel / Story": creative_score,
            "Data Sheet / Report": datasheet_score,
            "Standard Document": 1.0 # Baseline score
        }
        
        # Determine highest scoring document type
        best_type = max(scores, key=lambda k: scores[k])
        # If max score is 0, fall back to Standard Document
        if scores[best_type] == 0:
            result.document_type = "Standard Document"
        else:
            result.document_type = best_type

        # Filename recommendation
        if result.title != "Untitled":
            base_slug = cls.slugify(result.title)
            result.recommended_filename = f"{base_slug}.pdf"
        elif original_filename:
            path_orig = Path(original_filename)
            result.recommended_filename = f"{path_orig.stem}.pdf"
        else:
            result.recommended_filename = "mint_output.pdf"

        # Template and Style recommendations based on Document Type
        if result.document_type == "Technical Documentation":
            result.recommended_template = "Technical Report"
            result.recommended_theme = "Minimal"
            result.recommended_font = "Inter"
        elif result.document_type == "Data Sheet / Report":
            result.recommended_template = "Project Plan"
            result.recommended_theme = "Blue"
            result.recommended_font = "Calibri"
        elif result.document_type == "Academic Paper":
            result.recommended_template = "Thesis"
            result.recommended_theme = "Professional"
            result.recommended_font = "Times New Roman"
        elif result.document_type == "Creative Novel / Story":
            result.recommended_template = "Novel"
            result.recommended_theme = "Forest"
            result.recommended_font = "Georgia"
        else:
            result.recommended_template = "Standard"
            result.recommended_theme = "Professional"
            result.recommended_font = "Helvetica"

        return result
