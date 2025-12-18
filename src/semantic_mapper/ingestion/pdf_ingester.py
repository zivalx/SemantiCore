"""PDF data ingester."""

from typing import List

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from .base import BaseIngester
from ..models.ingestion import CanonicalRecord, IngestionResult, SourceType


class PDFIngester(BaseIngester):
    """Ingest PDF files into canonical format."""

    def __init__(self):
        super().__init__(SourceType.PDF)
        if PdfReader is None:
            raise ImportError("pypdf is required for PDF ingestion. Install with: pip install pypdf")

    def ingest(self, file_path: str, **kwargs) -> IngestionResult:
        """
        Ingest a PDF file.

        Extracts text content page by page.

        Args:
            file_path: Path to PDF file
            **kwargs:
                - extract_by: 'page' or 'document' (default: page)

        Returns:
            IngestionResult with canonical records
        """
        self._validate_file(file_path)

        extract_by = kwargs.get("extract_by", "page")
        errors: List[str] = []
        warnings: List[str] = []
        records: List[CanonicalRecord] = []

        try:
            provenance = self._create_provenance(file_path, extract_by=extract_by)

            reader = PdfReader(file_path)
            num_pages = len(reader.pages)

            if num_pages == 0:
                warnings.append("PDF has no pages")
                return IngestionResult(
                    provenance=provenance,
                    records=[],
                    record_count=0,
                    warnings=warnings,
                )

            if extract_by == "document":
                # Extract entire document as one record
                full_text = ""
                for page in reader.pages:
                    try:
                        full_text += page.extract_text() + "\n\n"
                    except Exception as e:
                        warnings.append(f"Failed to extract text from a page: {str(e)}")

                if full_text.strip():
                    record = self._create_record(
                        source_id=provenance.source_id,
                        record_index=0,
                        raw_content={"text": full_text, "num_pages": num_pages},
                        structured_fields={"content": full_text.strip(), "page_count": num_pages},
                        text_content=full_text.strip(),
                    )
                    records.append(record)
            else:
                # Extract page by page
                for idx, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            record = self._create_record(
                                source_id=provenance.source_id,
                                record_index=idx,
                                raw_content={"text": text, "page_number": idx + 1},
                                structured_fields={
                                    "content": text.strip(),
                                    "page_number": idx + 1,
                                    "length": len(text),
                                },
                                text_content=text.strip(),
                            )
                            records.append(record)
                        else:
                            warnings.append(f"Page {idx + 1} contains no text")
                    except Exception as e:
                        errors.append(f"Error extracting page {idx + 1}: {str(e)}")

            if not records:
                warnings.append("No text content extracted from PDF")

        except Exception as e:
            errors.append(f"Failed to ingest PDF: {str(e)}")

        return IngestionResult(
            provenance=provenance,
            records=records,
            record_count=len(records),
            errors=errors,
            warnings=warnings,
        )
