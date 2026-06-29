from mintpdf.domain.models import (
    CodeBlock,
    Configuration,
    Document,
    Heading,
    Image,
    Metadata,
    Page,
    Paragraph,
    Quote,
    Reference,
    Section,
    Table,
    Template,
    Theme,
)


def test_element_models():
    h = Heading(text="Heading", level=1)
    assert h.text == "Heading"
    assert h.level == 1

    p = Paragraph(text="Hello")
    assert p.text == "Hello"

    t = Table(headers=["A", "B"], rows=[["1", "2"]])
    assert t.headers == ["A", "B"]
    assert t.rows == [["1", "2"]]

    img = Image(path="img.png")
    assert img.path == "img.png"

    cb = CodeBlock(code="print(1)")
    assert cb.code == "print(1)"

    q = Quote(text="To be...")
    assert q.text == "To be..."

    ref = Reference(text="Reference text")
    assert ref.text == "Reference text"


def test_container_models():
    metadata = Metadata(title="My Doc", author="Me")
    section = Section(title="Intro", elements=[Paragraph("text")])
    page = Page(size="A4", margin_top=54, margin_bottom=54, margin_left=54, margin_right=54)

    doc = Document(metadata=metadata, sections=[section], page_settings=page)
    assert doc.metadata.title == "My Doc"
    assert doc.sections[0].title == "Intro"
    assert doc.page_settings.size == "A4"


def test_visual_models():
    theme = Theme(
        name="Dark", primary="#000000", secondary="#111111", accent="#222222", text="#ffffff"
    )
    assert theme.name == "Dark"
    assert theme.primary == "#000000"

    template = Template(name="Clean", description="Clean theme", category="General")
    assert template.name == "Clean"

    config = Configuration(
        output_dir="out",
        theme="Professional",
        default_template="Standard",
        default_font="Helvetica",
        page_size="LETTER",
        margins={"top": 54},
        language="English",
        auto_toc=True,
        auto_page_numbers=True,
    )
    assert config.theme == "Professional"
    assert config.margins == {"top": 54}
