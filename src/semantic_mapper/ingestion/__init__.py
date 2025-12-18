"""
Data ingestion module.

Handles ingestion of various data sources into canonical format.
"""

from .base import BaseIngester
from .csv_ingester import CSVIngester
from .json_ingester import JSONIngester
from .text_ingester import TextIngester
from .pdf_ingester import PDFIngester
from .docx_ingester import DOCXIngester
from .factory import IngesterFactory

__all__ = [
    "BaseIngester",
    "CSVIngester",
    "JSONIngester",
    "TextIngester",
    "PDFIngester",
    "DOCXIngester",
    "IngesterFactory",
]
