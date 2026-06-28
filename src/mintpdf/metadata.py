"""
Metadata schema for generated PDF documents.
Uses Pydantic for validation and easy dictionary conversion.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Container for PDF document metadata."""
    title: str = Field(
        default="Untitled Document",
        description="The primary title of the PDF document."
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="Secondary title or tagline."
    )
    author: Optional[str] = Field(
        default=None,
        description="The name of the document creator."
    )
    organization: Optional[str] = Field(
        default=None,
        description="The company, institution, or organization."
    )
    date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Document date (defaults to current date)."
    )
    version: str = Field(
        default="1.0.0",
        description="Document version identifier."
    )
    description: Optional[str] = Field(
        default=None,
        description="Short summary or description of the document."
    )
