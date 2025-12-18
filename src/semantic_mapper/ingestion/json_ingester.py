"""JSON data ingester."""

import json
from typing import Any, Dict, List

from .base import BaseIngester
from ..models.ingestion import CanonicalRecord, IngestionResult, SourceType


class JSONIngester(BaseIngester):
    """Ingest JSON files into canonical format."""

    def __init__(self):
        super().__init__(SourceType.JSON)

    def ingest(self, file_path: str, **kwargs) -> IngestionResult:
        """
        Ingest a JSON file.

        Handles both single objects and arrays of objects.

        Args:
            file_path: Path to JSON file
            **kwargs: Additional parameters (encoding, etc.)

        Returns:
            IngestionResult with canonical records
        """
        self._validate_file(file_path)

        encoding = kwargs.get("encoding", "utf-8")
        errors: List[str] = []
        warnings: List[str] = []
        records: List[CanonicalRecord] = []

        try:
            provenance = self._create_provenance(file_path, encoding=encoding)

            with open(file_path, "r", encoding=encoding) as f:
                data = json.load(f)

            # Normalize to list of records
            if isinstance(data, dict):
                # Single object - treat as one record
                data_list = [data]
            elif isinstance(data, list):
                data_list = data
            else:
                errors.append(f"Unexpected JSON type: {type(data)}")
                return IngestionResult(
                    provenance=provenance,
                    records=[],
                    record_count=0,
                    errors=errors,
                )

            for idx, item in enumerate(data_list):
                try:
                    if isinstance(item, dict):
                        # Extract structured fields (flatten one level)
                        structured = self._flatten_dict(item)

                        # Create text representation
                        text_content = json.dumps(item, indent=2)

                        record = self._create_record(
                            source_id=provenance.source_id,
                            record_index=idx,
                            raw_content=item,
                            structured_fields=structured,
                            text_content=text_content,
                        )
                        records.append(record)
                    else:
                        warnings.append(f"Skipping non-dict item at index {idx}: {type(item)}")
                except Exception as e:
                    errors.append(f"Error processing record {idx}: {str(e)}")

            if not records and not errors:
                warnings.append("JSON file contains no valid records")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to ingest JSON: {str(e)}")

        return IngestionResult(
            provenance=provenance,
            records=records,
            record_count=len(records),
            errors=errors,
            warnings=warnings,
        )

    def _flatten_dict(self, d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """
        Flatten nested dictionary one level.

        Only flattens simple nested dicts, not lists or deep nesting.
        """
        result = {}
        for key, value in d.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict) and not any(isinstance(v, (dict, list)) for v in value.values()):
                # Flatten one level only
                for sub_key, sub_value in value.items():
                    result[f"{new_key}.{sub_key}"] = sub_value
            elif isinstance(value, (str, int, float, bool, type(None))):
                result[new_key] = value
            else:
                # Keep complex values as JSON strings
                result[new_key] = json.dumps(value)

        return result
