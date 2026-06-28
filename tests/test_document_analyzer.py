import pytest
from mintpdf.document_analyzer import DocumentAnalyzer

def test_document_analyzer_atx():
    text = """# Main Document Title
    
Some body text paragraph here.

## Section 1
More info about this section.
"""
    result = DocumentAnalyzer.analyze(text)
    assert result.title == "Main Document Title"
    assert result.headings_count == 1
    assert result.subheadings_count == 1
    assert result.paragraphs_count == 1
    assert result.recommended_filename == "main_document_title.pdf"

def test_document_analyzer_setext():
    text = """Setext Title Underline
======================

Section 2 Underline
-------------------
Some paragraph content.
"""
    result = DocumentAnalyzer.analyze(text)
    assert result.title == "Setext Title Underline"
    assert result.headings_count == 1
    assert result.subheadings_count == 1
    assert result.recommended_filename == "setext_title_underline.pdf"

def test_document_analyzer_classification():
    technical_doc = """# Technical Spec
```python
def foo():
    pass
```
Let's check code blocks:
- List element 1
- List element 2
"""
    result = DocumentAnalyzer.analyze(technical_doc)
    assert result.document_type == "Technical Documentation"
    assert result.recommended_template == "Technical Report"
    assert result.recommended_theme == "Minimal"
    assert result.recommended_font == "Inter"
