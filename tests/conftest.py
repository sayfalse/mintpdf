
import pytest

from mintpdf.settings import AppSettings, MarginsSettings
from mintpdf.template_manager import Template
from mintpdf.theme_manager import Theme


@pytest.fixture
def mock_settings(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return AppSettings(
        output_dir=str(output_dir),
        theme="Professional",
        default_template="Standard",
        default_font="Helvetica",
        margins=MarginsSettings(top=54.0, bottom=54.0, left=54.0, right=54.0),
        auto_toc=True,
        auto_page_numbers=True,
    )


@pytest.fixture
def mock_theme():
    return Theme(
        name="Professional",
        primary="#2B6CB0",
        secondary="#1A365D",
        accent="#319795",
        text="#2D3748",
        bg="#FFFFFF",
        border="#E2E8F0",
        table_row_alt="#F7FAFC",
        link_color="#3182CE",
    )


@pytest.fixture
def mock_template():
    return Template(
        name="Standard",
        description="Standard report style",
        category="General",
        margins={"top": 54.0, "bottom": 54.0, "left": 54.0, "right": 54.0},
        typography={"body_font_size": 10.5, "body_leading": 15.0},
        heading_styles={
            "h1_size": 20.0,
            "h1_leading": 24.0,
            "h2_size": 15.0,
            "h2_leading": 19.0,
            "h3_size": 12.0,
            "h3_leading": 16.0,
        },
    )
