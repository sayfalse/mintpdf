import pytest
from mintpdf.utils import pt_to_inch, inch_to_pt, format_bytes, truncate_text

def test_pt_to_inch():
    assert pt_to_inch(72.0) == 1.0
    assert pt_to_inch(0.0) == 0.0

def test_inch_to_pt():
    assert inch_to_pt(1.0) == 72.0
    assert inch_to_pt(0.0) == 0.0

def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1024 * 1024) == "1.00 MB"

def test_truncate_text():
    assert truncate_text("hello", 10) == "hello"
    assert truncate_text("hello world", 5) == "hello..."
