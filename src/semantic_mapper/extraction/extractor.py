"""
Semantic extractor.

Provides utilities for working with canonical records in preparation for ontology generation.
The actual semantic interpretation happens in the LLM layer.
"""

from typing import List, Dict, Any
from collections import Counter

from ..models.ingestion import CanonicalRecord


class SemanticExtractor:
    """
    Utilities for analyzing canonical records.

    This is NOT a black-box ML extractor - it provides simple statistics
    and sampling to help the LLM make informed proposals.
    """

    @staticmethod
    def get_sample_records(
        records: List[CanonicalRecord],
        sample_size: int = 10,
        strategy: str = "diverse",
    ) -> List[CanonicalRecord]:
        """
        Get sample records for ontology proposal.

        Args:
            records: All canonical records
            sample_size: Number of samples to return
            strategy: Sampling strategy ("diverse", "random", "first")

        Returns:
            Sample records
        """
        if len(records) <= sample_size:
            return records

        if strategy == "first":
            return records[:sample_size]
        elif strategy == "random":
            import random
            return random.sample(records, sample_size)
        else:  # diverse
            # Simple diversity: spread samples across the dataset
            step = len(records) // sample_size
            return [records[i * step] for i in range(sample_size)]

    @staticmethod
    def analyze_field_patterns(
        records: List[CanonicalRecord],
    ) -> Dict[str, Any]:
        """
        Analyze patterns in record fields.

        Returns statistics about field names, types, and values
        to help guide ontology proposal.

        Args:
            records: Canonical records

        Returns:
            Analysis results
        """
        field_stats = {}
        all_fields = []

        for record in records:
            for field_name, field_value in record.structured_fields.items():
                all_fields.append(field_name)

                if field_name not in field_stats:
                    field_stats[field_name] = {
                        "count": 0,
                        "sample_values": [],
                        "types": Counter(),
                    }

                field_stats[field_name]["count"] += 1
                field_stats[field_name]["types"][type(field_value).__name__] += 1

                # Collect sample values
                if len(field_stats[field_name]["sample_values"]) < 5:
                    field_stats[field_name]["sample_values"].append(field_value)

        # Field frequency
        field_frequency = Counter(all_fields)

        return {
            "total_records": len(records),
            "unique_fields": len(field_stats),
            "field_frequency": dict(field_frequency),
            "field_stats": field_stats,
        }

    @staticmethod
    def get_text_samples(
        records: List[CanonicalRecord],
        sample_size: int = 5,
    ) -> List[str]:
        """
        Get text content samples.

        Args:
            records: Canonical records
            sample_size: Number of samples

        Returns:
            List of text samples
        """
        text_samples = []
        for record in records:
            if record.text_content:
                text_samples.append(record.text_content)
                if len(text_samples) >= sample_size:
                    break

        return text_samples
