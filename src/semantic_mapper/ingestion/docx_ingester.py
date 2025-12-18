"""DOCX data ingester."""

from typing import List

try:
    from docx import Document
except ImportError:
    Document = None

from .base import BaseIngester
from ..models.ingestion import CanonicalRecord, IngestionResult, SourceType


class DOCXIngester(BaseIngester):
    """Ingest DOCX files into canonical format."""

    def __init__(self):
        super().__init__(SourceType.DOCX)
        if Document is None:
            raise ImportError(
                "python-docx is required for DOCX ingestion. Install with: pip install python-docx"
            )

    def ingest(self, file_path: str, **kwargs) -> IngestionResult:
        """
        Ingest a DOCX file.

        Extracts text content paragraph by paragraph.

        Args:
            file_path: Path to DOCX file
            **kwargs:
                - extract_by: 'paragraph' or 'document' (default: paragraph)

        Returns:
            IngestionResult with canonical records
        """
        self._validate_file(file_path)

        extract_by = kwargs.get("extract_by", "paragraph")
        errors: List[str] = []
        warnings: List[str] = []
        records: List[CanonicalRecord] = []

        try:
            provenance = self._create_provenance(file_path, extract_by=extract_by)

            doc = Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

            if not paragraphs:
                warnings.append("DOCX contains no text paragraphs")
                return IngestionResult(
                    provenance=provenance,
                    records=[],
                    record_count=0,
                    warnings=warnings,
                )

            if extract_by == "document":
                # Combine all paragraphs into one record
                full_text = "\n\n".join(paragraphs)
                record = self._create_record(
                    source_id=provenance.source_id,
                    record_index=0,
                    raw_content={"text": full_text, "paragraph_count": len(paragraphs)},
                    structured_fields={
                        "content": full_text,
                        "paragraph_count": len(paragraphs),
                    },
                    text_content=full_text,
                )
                records.append(record)
            else:
                # Extract paragraph by paragraph
                for idx, para_text in enumerate(paragraphs):
                    record = self._create_record(
                        source_id=provenance.source_id,
                        record_index=idx,
                        raw_content={"text": para_text, "paragraph_number": idx + 1},
                        structured_fields={
                            "content": para_text,
                            "paragraph_number": idx + 1,
                            "length": len(para_text),
                        },
                        text_content=para_text,
                    )
                    records.append(record)

        except Exception as e:
            errors.append(f"Failed to ingest DOCX: {str(e)}")

        return IngestionResult(
            provenance=provenance,
            records=records,
            record_count=len(records),
            errors=errors,
            warnings=warnings,
        )
