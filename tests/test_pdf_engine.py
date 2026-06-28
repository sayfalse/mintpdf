
from mintpdf.metadata import DocumentMetadata
from mintpdf.pdf_engine import generate_pdf


def test_generate_pdf_end_to_end(mock_settings, tmp_path):
    metadata = DocumentMetadata(
        title="PDF Generation Unit Test",
        author="Mint PDF Test Harness",
        description="Verifies that standard ReportLab compiles cleanly",
    )

    output_file = tmp_path / "test_doc.pdf"
    content = """# Verification Heading
This is some verification body copy.
"""
    success = generate_pdf(
        text=content,
        output_path=output_file,
        metadata=metadata,
        settings=mock_settings,
        has_cover=True,
    )

    assert success
    assert output_file.exists()
    assert output_file.stat().st_size > 0
