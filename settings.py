"""
Settings and configuration schemas for Mint PDF.
Uses Pydantic for validation, structured parsing, and default merging.
"""

from typing import Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class PageSizeEnum(str, Enum):
    LETTER = "LETTER"
    A4 = "A4"
    LEGAL = "LEGAL"
    A3 = "A3"
    A5 = "A5"

class ThemeEnum(str, Enum):
    BLUE = "Blue"
    GREEN = "Green"
    PURPLE = "Purple"
    GRAY = "Gray"
    BLACK = "Black"
    WHITE = "White"
    OCEAN = "Ocean"
    FOREST = "Forest"
    PROFESSIONAL = "Professional"
    MINIMAL = "Minimal"

class FontEnum(str, Enum):
    TIMES_NEW_ROMAN = "Times New Roman"
    ARIAL = "Arial"
    CALIBRI = "Calibri"
    HELVETICA = "Helvetica"
    GEORGIA = "Georgia"
    GARAMOND = "Garamond"
    ROBOTO = "Roboto"
    OPEN_SANS = "Open Sans"
    LATO = "Lato"
    INTER = "Inter"

class MarginsSettings(BaseModel):
    """Document margin settings in points (1 inch = 72 points)."""
    top: float = Field(default=54.0, description="Top margin in points")
    bottom: float = Field(default=54.0, description="Bottom margin in points")
    left: float = Field(default=54.0, description="Left margin in points")
    right: float = Field(default=54.0, description="Right margin in points")

    @field_validator("top", "bottom", "left", "right")
    @classmethod
    def validate_margin(cls, value: float) -> float:
        """Ensure margins are non-negative and within reasonable bounds."""
        if value < 0:
            raise ValueError("Margin must be a non-negative number.")
        if value > 500:
            raise ValueError("Margin is too large (maximum 500 points).")
        return value

class AppSettings(BaseModel):
    """Core settings schema for the Mint PDF application."""
    config_version: int = Field(
        default=1,
        description="Configuration schema version for automatic migrations."
    )
    output_dir: str = Field(
        default="",
        description="Path to the directory where generated PDFs are saved."
    )
    theme: ThemeEnum = Field(
        default=ThemeEnum.PROFESSIONAL,
        description="Default visual theme for documents."
    )
    default_template: str = Field(
        default="Standard",
        description="Default layout template."
    )
    default_font: FontEnum = Field(
        default=FontEnum.HELVETICA,
        description="Default document font family."
    )
    page_size: PageSizeEnum = Field(
        default=PageSizeEnum.LETTER,
        description="Standard page dimensions."
    )
    margins: MarginsSettings = Field(
        default_factory=MarginsSettings,
        description="Page margin configuration."
    )
    language: str = Field(
        default="English",
        description="Default interface and hyphenation language."
    )
    auto_toc: bool = Field(
        default=True,
        description="If True, automatically build and insert a Table of Contents."
    )
    auto_page_numbers: bool = Field(
        default=True,
        description="If True, print page numbers in the footer."
    )

    @field_validator("theme", mode="before")
    @classmethod
    def validate_theme_before(cls, value: Any) -> Any:
        """Resolve theme case-insensitively to its matching Enum value."""
        if isinstance(value, str):
            val_lower = value.strip().lower()
            for enum_val in ThemeEnum:
                if enum_val.value.lower() == val_lower:
                    return enum_val
        return value

    @field_validator("default_font", mode="before")
    @classmethod
    def validate_font_before(cls, value: Any) -> Any:
        """Resolve font family case-insensitively to its matching Enum value."""
        if isinstance(value, str):
            val_lower = value.strip().lower()
            for enum_val in FontEnum:
                if enum_val.value.lower() == val_lower:
                    return enum_val
        return value

    @field_validator("page_size", mode="before")
    @classmethod
    def validate_page_size_before(cls, value: Any) -> Any:
        """Resolve page size case-insensitively to its matching Enum value."""
        if isinstance(value, str):
            val_upper = value.strip().upper()
            for enum_val in PageSizeEnum:
                if enum_val.value == val_upper:
                    return enum_val
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings model into a standard dictionary."""
        # Convert enums to their raw string values
        data = self.model_dump()
        data["theme"] = self.theme.value
        data["default_font"] = self.default_font.value
        data["page_size"] = self.page_size.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        """Instantiate settings model from a dictionary."""
        return cls(**data)

    @classmethod
    def from_dict_with_defaults(cls, data: Dict[str, Any]) -> "AppSettings":
        """
        Instantiates settings by merging input data over defaults.
        Safely ignores invalid values or incompatible keys.
        """
        # Start with default dictionary
        defaults = cls().model_dump()
        
        # Merge values
        merged = {}
        for key, default_val in defaults.items():
            if key in data:
                # Merge sub-dictionary (margins)
                if isinstance(default_val, dict) and isinstance(data[key], dict):
                    sub_merged = {**default_val}
                    for sub_key, sub_default in default_val.items():
                        if sub_key in data[key]:
                            try:
                                # Cast to type of default to check type compatibility
                                sub_merged[sub_key] = type(sub_default)(data[key][sub_key])
                            except (ValueError, TypeError):
                                pass # Keep default
                    merged[key] = sub_merged
                else:
                    # Check for enum value compatibility
                    if key == "theme":
                        try:
                            # Verify if value matches Enum values
                            val = data[key]
                            # Handle string casing normalization
                            normalized = val.strip().title()
                            ThemeEnum(normalized)
                            merged[key] = normalized
                        except ValueError:
                            merged[key] = default_val
                    elif key == "default_font":
                        try:
                            val = data[key]
                            # Exact match or title case fallback
                            try:
                                FontEnum(val)
                                merged[key] = val
                            except ValueError:
                                normalized = val.strip().title()
                                FontEnum(normalized)
                                merged[key] = normalized
                        except ValueError:
                            merged[key] = default_val
                    elif key == "page_size":
                        try:
                            val = str(data[key]).upper().strip()
                            PageSizeEnum(val)
                            merged[key] = val
                        except ValueError:
                            merged[key] = default_val
                    else:
                        # Standard type matching
                        try:
                            merged[key] = type(default_val)(data[key])
                        except (ValueError, TypeError):
                            merged[key] = default_val
            else:
                merged[key] = default_val

        try:
            return cls(**merged)
        except Exception:
            # Fallback to fresh default instance if initialization fails
            return cls()
