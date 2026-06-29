from mintpdf.services import (
    ConfigurationService,
    CoverPageService,
    DocumentAnalysisService,
    ExportService,
    FontService,
    MetadataService,
    TemplateService,
    ThemeService,
    TOCService,
)


def test_services_instantiation():
    config_service = ConfigurationService()
    theme_service = ThemeService()
    template_service = TemplateService()
    font_service = FontService()
    analysis_service = DocumentAnalysisService()
    metadata_service = MetadataService()
    cover_page_service = CoverPageService()
    toc_service = TOCService()
    export_service = ExportService()

    assert config_service is not None
    assert theme_service is not None
    assert template_service is not None
    assert font_service is not None
    assert analysis_service is not None
    assert metadata_service is not None
    assert cover_page_service is not None
    assert toc_service is not None
    assert export_service is not None


def test_theme_service():
    service = ThemeService()
    names = service.get_all_theme_names()
    assert "Professional" in names

    t = service.get_theme("Professional")
    assert t.name == "Professional"
    assert t.primary == "#1B2A4A"


def test_template_service():
    service = TemplateService()
    names = service.get_template_names()
    assert "Standard" in names

    t = service.get_template("Standard")
    assert t.name == "Standard"


def test_font_service():
    service = FontService()
    fonts = service.get_supported_fonts()
    assert "Helvetica" in fonts
    assert service.get_safe_font_name("Helvetica") == "Helvetica"


def test_document_analysis_service():
    service = DocumentAnalysisService()
    res = service.analyze("# This is a simple title\n\nSome paragraph content here.", "doc.md")
    assert res.title == "This is a simple title"
    assert res.document_type == "Standard Document"


def test_metadata_service():
    service = MetadataService()
    meta = service.create_metadata(title="Test title", author="John Doe")
    assert meta.title == "Test title"
    assert meta.author == "John Doe"


def test_toc_service():
    service = TOCService()
    headings = service.extract_headings("# Heading 1\n## Heading 2")
    assert len(headings) == 2
    assert headings[0] == (1, "Heading 1")
    assert headings[1] == (2, "Heading 2")
