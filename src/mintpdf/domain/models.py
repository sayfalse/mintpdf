from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Heading:
    """Domain model representing a document heading element."""

    text: str
    level: int  # 1, 2, or 3


@dataclass
class Paragraph:
    """Domain model representing a paragraph element."""

    text: str


@dataclass
class Table:
    """Domain model representing a table element."""

    headers: List[str]
    rows: List[List[str]]


@dataclass
class Image:
    """Domain model representing an image element."""

    path: str
    width: Optional[float] = None
    height: Optional[float] = None
    caption: Optional[str] = None


@dataclass
class CodeBlock:
    """Domain model representing a code block element."""

    code: str
    language: Optional[str] = None


@dataclass
class Quote:
    """Domain model representing a blockquote element."""

    text: str


@dataclass
class Reference:
    """Domain model representing a citation/reference element."""

    text: str


@dataclass
class Section:
    """Domain model representing a section containing elements."""

    title: Optional[str] = None
    elements: List[Any] = field(default_factory=list)


@dataclass
class Metadata:
    """Domain model representing PDF document metadata."""

    title: str = "Untitled Document"
    subtitle: Optional[str] = None
    author: Optional[str] = None
    organization: Optional[str] = None
    date: Optional[str] = None
    version: str = "1.0.0"
    description: Optional[str] = None


@dataclass
class Page:
    """Domain model representing page geometry, size, margins and header/footer configurations."""

    size: str
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float
    header_text: Optional[str] = None
    footer_text: Optional[str] = None


@dataclass
class Document:
    """Domain model representing the entire structured document."""

    metadata: Metadata
    sections: List[Section] = field(default_factory=list)
    page_settings: Optional[Page] = None


@dataclass
class Theme:
    """Domain model representing document visual color themes."""

    name: str
    primary: str
    secondary: str
    accent: str
    text: str
    bg: str = "#FFFFFF"
    border: str = "#E2E8F0"
    table_header_bg: Optional[str] = None
    table_row_alt: str = "#F7FAFC"
    link_color: str = "#3182CE"


@dataclass
class Template:
    """Domain model representing page layout, margins, and typography styles."""

    name: str
    description: str
    category: str
    extends: Optional[str] = None
    margins: Optional[Dict[str, float]] = None
    typography: Optional[Dict[str, Any]] = None
    heading_styles: Optional[Dict[str, Any]] = None


@dataclass
class Configuration:
    """Domain model representing global application configurations."""

    output_dir: str
    theme: str
    default_template: str
    default_font: str
    page_size: str
    margins: Dict[str, float]
    language: str
    auto_toc: bool
    auto_page_numbers: bool
