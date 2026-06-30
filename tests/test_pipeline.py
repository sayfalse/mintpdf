from mintpdf.domain.models import Metadata, Template, Theme
from mintpdf.pipeline import (
    DocumentBuilder,
    DocumentLoader,
    LayoutBuilder,
    PDFExporter,
    Renderer,
)
from mintpdf.settings import AppSettings


def test_document_loader(tmp_path):
    loader = DocumentLoader()
    doc_file = tmp_path / "test.md"
    doc_file.write_text("Hello, world!", encoding="utf-8")
    content = loader.load(doc_file)
    assert content == "Hello, world!"


def test_document_builder():
    builder = DocumentBuilder()
    meta = Metadata(title="Test title")
    text = (
        "# Main Heading\n\n"
        "Some paragraph here.\n\n"
        "## Sub heading\n\n"
        "```python\n"
        "print('hello')\n"
        "```\n\n"
        "> A quote statement\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "- Item 1\n"
        "- Item 2\n"
    )
    doc = builder.build(text, meta)
    assert doc.metadata.title == "Test title"
    assert len(doc.sections) == 1

    elements = doc.sections[0].elements
    # heading, paragraph, subheading, codeblock, quote, table, list paragraphs
    assert any(h.text == "Main Heading" for h in elements if hasattr(h, "text"))


def test_layout_builder():
    builder = LayoutBuilder()
    settings = AppSettings()
    template = Template(
        name="Custom", description="desc", category="General", margins={"top": 45.0}
    )
    page = builder.build_layout(settings, template)
    assert page.margin_top == 45.0
    assert page.size == "LETTER"


def test_renderer_and_exporter(tmp_path):
    meta = Metadata(title="Pipeline PDF Test")
    document = DocumentBuilder().build("# Heading 1\nHello, world!", meta)
    theme = Theme(
        name="Dark", primary="#000000", secondary="#111111", accent="#222222", text="#ffffff"
    )
    template = Template(name="Custom", description="desc", category="General")

    renderer = Renderer()
    flowables = renderer.render(document, theme, template)
    assert len(flowables) > 0

    exporter = PDFExporter()
    out_pdf = tmp_path / "pipeline_out.pdf"
    settings = AppSettings()
    success = exporter.export(flowables, out_pdf, document, settings, theme, has_cover=False)
    assert success is True
    assert out_pdf.exists()
