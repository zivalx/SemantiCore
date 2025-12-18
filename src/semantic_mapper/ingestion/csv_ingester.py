"""CSV data ingester."""

import csv
from typing import Any, Dict, List

from .base import BaseIngester
from ..models.ingestion import CanonicalRecord, IngestionResult, SourceType


class CSVIngester(BaseIngester):
    """Ingest CSV files into canonical format."""

    def __init__(self):
        super().__init__(SourceType.CSV)

    def ingest(self, file_path: str, **kwargs) -> IngestionResult:
        """
        Ingest a CSV file.

        Args:
            file_path: Path to CSV file
            **kwargs: Additional parameters (delimiter, encoding, etc.)

        Returns:
            IngestionResult with canonical records
        """
        self._validate_file(file_path)

        delimiter = kwargs.get("delimiter", ",")
        encoding = kwargs.get("encoding", "utf-8")
        errors: List[str] = []
        warnings: List[str] = []
        records: List[CanonicalRecord] = []

        try:
            provenance = self._create_provenance(
                file_path, delimiter=delimiter, encoding=encoding
            )

            with open(file_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                # Check if file is empty
                try:
                    fieldnames = reader.fieldnames
                    if not fieldnames:
                        errors.append("CSV file has no columns")
                        return IngestionResult(
                            provenance=provenance,
                            records=[],
                            record_count=0,
                            errors=errors,
                        )
                except Exception as e:
                    errors.append(f"Failed to read CSV headers: {str(e)}")
                    return IngestionResult(
                        provenance=provenance,
                        records=[],
                        record_count=0,
                        errors=errors,
                    )

                for idx, row in enumerate(reader):
                    try:
                        # Filter out empty values
                        structured = {k: v for k, v in row.items() if v and v.strip()}

                        # Create text representation
                        text_parts = [f"{k}: {v}" for k, v in structured.items()]
                        text_content = " | ".join(text_parts)

                        record = self._create_record(
                            source_id=provenance.source_id,
                            record_index=idx,
                            raw_content=row,
                            structured_fields=structured,
                            text_content=text_content,
                        )
                        records.append(record)
                    except Exception as e:
                        errors.append(f"Error processing row {idx}: {str(e)}")

            if not records and not errors:
                warnings.append("CSV file contains no data rows")

        except Exception as e:
            errors.append(f"Failed to ingest CSV: {str(e)}")

        return IngestionResult(
            provenance=provenance,
            records=records,
            record_count=len(records),
            errors=errors,
            warnings=warnings,
        )
