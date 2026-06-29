from typing import Optional

from ..metadata import DocumentMetadata


class MetadataService:
    """Service to manage document metadata."""

    def create_metadata(
        self,
        title: str,
        subtitle: Optional[str] = None,
        author: Optional[str] = None,
        organization: Optional[str] = None,
        date: Optional[str] = None,
        version: str = "1.0.0",
        description: Optional[str] = None,
    ) -> DocumentMetadata:
        kwargs = {
            "title": title,
            "subtitle": subtitle,
            "author": author,
            "organization": organization,
            "version": version,
            "description": description,
        }
        if date is not None:
            kwargs["date"] = date
        return DocumentMetadata(**kwargs)
