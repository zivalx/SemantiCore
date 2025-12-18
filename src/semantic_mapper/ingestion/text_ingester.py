"""Plain text data ingester."""

from typing import List

from .base import BaseIngester
from ..models.ingestion import CanonicalRecord, IngestionResult, SourceType


class TextIngester(BaseIngester):
    """Ingest plain text files into canonical format."""

    def __init__(self):
        super().__init__(SourceType.TEXT)

    def ingest(self, file_path: str, **kwargs) -> IngestionResult:
        """
        Ingest a text file.

        Can split by paragraphs, lines, or treat as single document.

        Args:
            file_path: Path to text file
            **kwargs:
                - encoding: File encoding (default: utf-8)
                - split_by: 'paragraph', 'line', or 'document' (default: paragraph)

        Returns:
            IngestionResult with canonical records
        """
        self._validate_file(file_path)

        encoding = kwargs.get("encoding", "utf-8")
        split_by = kwargs.get("split_by", "paragraph")
        errors: List[str] = []
        warnings: List[str] = []
        records: List[CanonicalRecord] = []

        try:
            provenance = self._create_provenance(
                file_path, encoding=encoding, split_by=split_by
            )

            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()

            if not content.strip():
                warnings.append("Text file is empty")
                return IngestionResult(
                    provenance=provenance,
                    records=[],
                    record_count=0,
                    warnings=warnings,
                )

            # Split content based on strategy
            if split_by == "document":
                chunks = [content]
            elif split_by == "line":
                chunks = [line for line in content.split("\n") if line.strip()]
            else:  # paragraph
                chunks = [p for p in content.split("\n\n") if p.strip()]

            for idx, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if not chunk:
                    continue

                record = self._create_record(
                    source_id=provenance.source_id,
                    record_index=idx,
                    raw_content={"text": chunk},
                    structured_fields={"content": chunk, "length": len(chunk)},
                    text_content=chunk,
                )
                records.append(record)

            if not records:
                warnings.append("No text content extracted")

        except Exception as e:
            errors.append(f"Failed to ingest text: {str(e)}")

        return IngestionResult(
            provenance=provenance,
            records=records,
            record_count=len(records),
            errors=errors,
            warnings=warnings,
        )
