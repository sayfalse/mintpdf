from reportlab.platypus import Paragraph, Table

from mintpdf.formatter import convert_markdown_inline, format_text_to_flowables


def test_convert_markdown_inline():
    # Test bold, italic, code
    text = "This is **bold** and *italic* and `code` text."
    result = convert_markdown_inline(text)
    assert "<b>bold</b>" in result
    assert "<i>italic</i>" in result
    assert '<font face="Courier" color="#805AD5"><b>code</b></font>' in result

    # Test links
    link_text = "Check [Github](https://github.com)"
    link_result = convert_markdown_inline(link_text)
    assert '<a href="https://github.com" color="#3182CE"><u>Github</u></a>' in link_result

    # Test snake_case variables in inline code (underscores should not be parsed as italics)
    snake_text = "Edit `config.json` to set defaults (e.g., `output_dir`, `page_size`)."
    snake_result = convert_markdown_inline(snake_text)
    assert "<i>" not in snake_result
    assert "output_dir" in snake_result
    assert "page_size" in snake_result


def test_format_text_to_flowables_table(mock_theme, mock_template):
    table_markdown = """
| Header 1 | Header 2 |
|----------|----------|
| Row 1 Col 1 | Row 1 Col 2 |
"""
    flowables = format_text_to_flowables(table_markdown, mock_theme, mock_template)

    # Assert that it returns at least one Table flowable
    tables = [f for f in flowables if isinstance(f, Table)]
    assert len(tables) == 1

    # Verify that cells are wrapped in Paragraph flowables
    table_obj = tables[0]
    data = table_obj._cellvalues
    assert len(data) == 2  # Header row and 1 data row
    assert isinstance(data[0][0], Paragraph)
    assert isinstance(data[1][0], Paragraph)


def test_format_text_to_flowables_nested_list(mock_theme, mock_template):
    list_markdown = """
- Level 1 Item
  - Level 2 Item
    - Level 3 Item
"""
    flowables = format_text_to_flowables(list_markdown, mock_theme, mock_template)
    paragraphs = [f for f in flowables if isinstance(f, Paragraph)]

    assert len(paragraphs) == 3
    # Check leftIndent styles derived from indentation levels
    assert paragraphs[0].style.leftIndent == 15  # Level 1 (0 spaces // 2 -> level 0 -> 15 + 0 = 15)
    assert (
        paragraphs[1].style.leftIndent == 30
    )  # Level 2 (2 spaces // 2 -> level 1 -> 15 + 15 = 30)
    assert (
        paragraphs[2].style.leftIndent == 45
    )  # Level 3 (4 spaces // 2 -> level 2 -> 15 + 30 = 45)
