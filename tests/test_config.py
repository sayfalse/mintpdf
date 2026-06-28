import pytest
from pydantic import ValidationError

from mintpdf.settings import AppSettings, FontEnum, MarginsSettings, PageSizeEnum, ThemeEnum


def test_settings_validation():
    # Valid initializations
    s = AppSettings(theme="Professional", default_font="Helvetica", page_size="LETTER")
    assert s.theme == ThemeEnum.PROFESSIONAL
    assert s.default_font == FontEnum.HELVETICA
    assert s.page_size == PageSizeEnum.LETTER

    # Invalid values should raise ValidationError or handle case-insensitivity
    # Case-insensitive resolution check (from our validator)
    s2 = AppSettings(default_font="roboto", theme="forest")
    assert s2.default_font == FontEnum.ROBOTO
    assert s2.theme == ThemeEnum.FOREST

    # Margins constraint validation
    with pytest.raises(ValidationError):
        MarginsSettings(top=-10.0)


def test_from_dict_with_defaults():
    # Empty dictionary should return defaults
    s = AppSettings.from_dict_with_defaults({})
    assert s.theme == ThemeEnum.PROFESSIONAL
    assert s.default_font == FontEnum.HELVETICA

    # Partial merge with invalid types
    data = {
        "theme": "INVALID_THEME",
        "default_font": "lato",
        "margins": {"left": -20.0, "top": 40.0},  # invalid left margin
    }
    s2 = AppSettings.from_dict_with_defaults(data)
    assert s2.theme == ThemeEnum.PROFESSIONAL  # fell back to default
    assert s2.default_font == FontEnum.LATO  # resolved case-insensitively
    assert s2.margins.left == 54.0  # fell back to default due to invalid value
    assert s2.margins.top == 40.0  # successfully merged
