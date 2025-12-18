"""
Base ingester class.

Defines the interface for all data ingesters.
"""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from ..models.ingestion import (
    CanonicalRecord,
    IngestionResult,
    ProvenanceMetadata,
    SourceType,
)


class BaseIngester(ABC):
    """
    Abstract base class for all data ingesters.

    Ingesters transform raw data into canonical records.
    They do NOT infer semantics — that happens later.
    """

    def __init__(self, source_type: SourceType):
        self.source_type = source_type

    @abstractmethod
    def ingest(self, file_path: str, **kwargs) -> IngestionResult:
        """
        Ingest a data source and return canonical records.

        Args:
            file_path: Path to the data source
            **kwargs: Additional ingestion parameters

        Returns:
            IngestionResult with canonical records and metadata
        """
        pass

    def _create_provenance(self, file_path: str, **metadata) -> ProvenanceMetadata:
        """Create provenance metadata for a data source."""
        path = Path(file_path)

        # Calculate file checksum
        checksum = None
        if path.exists():
            with open(path, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

        return ProvenanceMetadata(
            source_type=self.source_type,
            source_name=path.name,
            file_path=str(path.absolute()),
            file_size_bytes=path.stat().st_size if path.exists() else None,
            checksum=checksum,
            additional_metadata=metadata,
        )

    def _create_record(
        self,
        source_id,
        record_index: int,
        raw_content: Dict[str, Any],
        structured_fields: Dict[str, Any] = None,
        text_content: str = None,
    ) -> CanonicalRecord:
        """Create a canonical record."""
        return CanonicalRecord(
            source_id=source_id,
            record_index=record_index,
            raw_content=raw_content,
            structured_fields=structured_fields or {},
            text_content=text_content,
        )

    def _validate_file(self, file_path: str) -> None:
        """Validate that the file exists and is readable."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
