"""Ingester factory for creating appropriate ingesters based on file type."""

from pathlib import Path
from typing import Optional

from .base import BaseIngester
from .csv_ingester import CSVIngester
from .json_ingester import JSONIngester
from .text_ingester import TextIngester
from .pdf_ingester import PDFIngester
from .docx_ingester import DOCXIngester
from ..models.ingestion import SourceType


class IngesterFactory:
    """Factory for creating appropriate ingesters."""

    _EXTENSION_MAP = {
        ".csv": CSVIngester,
        ".json": JSONIngester,
        ".jsonl": JSONIngester,
        ".txt": TextIngester,
        ".md": TextIngester,
        ".pdf": PDFIngester,
        ".docx": DOCXIngester,
    }

    _TYPE_MAP = {
        SourceType.CSV: CSVIngester,
        SourceType.JSON: JSONIngester,
        SourceType.TEXT: TextIngester,
        SourceType.PDF: PDFIngester,
        SourceType.DOCX: DOCXIngester,
    }

    @classmethod
    def create_from_file(cls, file_path: str) -> BaseIngester:
        """
        Create an ingester based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            Appropriate ingester instance

        Raises:
            ValueError: If file type is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        ingester_class = cls._EXTENSION_MAP.get(extension)
        if ingester_class is None:
            supported = ", ".join(cls._EXTENSION_MAP.keys())
            raise ValueError(
                f"Unsupported file type: {extension}. Supported types: {supported}"
            )

        return ingester_class()

    @classmethod
    def create_from_type(cls, source_type: SourceType) -> BaseIngester:
        """
        Create an ingester based on source type.

        Args:
            source_type: Type of data source

        Returns:
            Appropriate ingester instance

        Raises:
            ValueError: If source type is not supported
        """
        ingester_class = cls._TYPE_MAP.get(source_type)
        if ingester_class is None:
            supported = ", ".join([t.value for t in SourceType])
            raise ValueError(
                f"Unsupported source type: {source_type}. Supported types: {supported}"
            )

        return ingester_class()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return list(cls._EXTENSION_MAP.keys())

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if a file type is supported."""
        extension = Path(file_path).suffix.lower()
        return extension in cls._EXTENSION_MAP
