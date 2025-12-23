"""
Extraction Service.

Wraps existing semantic_mapper ingestion and extraction logic.
Extracts semantic primitives (entities, attributes, relations) from uploaded sources.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import sys
import os

# Add paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
sys.path.append(os.path.join(backend_dir, "..", "src"))

from semantic_mapper.ingestion.factory import IngesterFactory
from semantic_mapper.extraction.extractor import SemanticExtractor
from semantic_mapper.llm.base import BaseLLMProvider
from db.models import Job, JobType, JobStatus, Source, Primitive, PrimitiveType


class ExtractionService:
    """
    Service for extracting semantic primitives from sources.

    Flow:
    1. Ingest sources to canonical records
    2. Sample and analyze data
    3. Use LLM to extract semantic primitives (entities, attributes, relations)
    4. Store primitives in PostgreSQL
    """

    def __init__(self, db: Session, llm: BaseLLMProvider):
        self.db = db
        self.llm = llm

    def create_extraction_job(self, project_id: UUID) -> Job:
        """Create a new extraction job."""
        job = Job(
            project_id=project_id, type=JobType.EXTRACTION, status=JobStatus.PENDING
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_extraction(self, job_id: UUID, project_id: UUID):
        """
        Execute extraction job (background task).

        Steps:
        1. Load all sources for project
        2. Ingest each source to canonical records
        3. Extract semantic primitives using LLM
        4. Store primitives in database
        """
        try:
            # Update job status
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.progress = 0.0
            self.db.commit()

            # Load sources
            sources = (
                self.db.query(Source).filter(Source.project_id == project_id).all()
            )

            if not sources:
                job.status = JobStatus.FAILED
                job.error = "No sources found for project"
                job.completed_at = datetime.utcnow()
                self.db.commit()
                return

            all_records = []
            source_mapping = {}  # Map record index to source_id

            # Ingest all sources
            for idx, source in enumerate(sources):
                try:
                    # Use existing ingester factory
                    ingester = IngesterFactory.create_from_file(source.file_path)
                    result = ingester.ingest(source.file_path)

                    # Track which records came from which source
                    start_idx = len(all_records)
                    all_records.extend(result.records)
                    end_idx = len(all_records)

                    for i in range(start_idx, end_idx):
                        source_mapping[i] = source.id

                    # Update source metadata
                    source.canonical_record_count = len(result.records)
                    source.ingestion_job_id = job_id

                    # Update progress
                    progress = ((idx + 1) / len(sources)) * 50  # Ingestion is 50% of work
                    job.progress = progress
                    self.db.commit()

                except Exception as e:
                    print(f"Error ingesting source {source.name}: {e}")
                    continue

            if not all_records:
                job.status = JobStatus.FAILED
                job.error = "No records ingested from sources"
                job.completed_at = datetime.utcnow()
                self.db.commit()
                return

            # Extract semantic primitives using LLM
            primitives_data = self._extract_primitives_with_llm(all_records, project_id)

            # Store primitives in database
            for prim_data in primitives_data:
                # Get source_id from record_index if available
                record_idx = prim_data.get("record_index", 0)
                source_id = source_mapping.get(record_idx, sources[0].id)

                primitive = Primitive(
                    project_id=project_id,
                    source_id=source_id,
                    label=prim_data["label"],
                    type=PrimitiveType(prim_data["type"]),
                    evidence=prim_data.get("evidence", ""),
                    confidence=prim_data.get("confidence", 0.8),
                    extraction_job_id=job_id,
                )
                self.db.add(primitive)

            # Complete job
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            job.result = {
                "primitive_count": len(primitives_data),
                "record_count": len(all_records),
                "source_count": len(sources),
            }
            self.db.commit()

        except Exception as e:
            # Handle errors
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Extraction job {job_id} failed: {e}")

    def _extract_primitives_with_llm(
        self, records: list, project_id: UUID
    ) -> list[dict]:
        """
        Use LLM to extract semantic primitives from records.

        This is a simplified extraction that identifies entities, attributes,
        and relationships before full ontology generation.
        """
        # Sample records for analysis
        samples = SemanticExtractor.get_sample_records(records, sample_size=10)

        # Analyze field patterns
        field_patterns = SemanticExtractor.analyze_field_patterns(records)

        # Build prompt for primitive extraction
        prompt = self._build_primitive_extraction_prompt(samples, field_patterns)

        try:
            # Use LLM to extract primitives
            response = self.llm.generate_text(
                prompt=prompt,
                system_prompt="You are a semantic analysis expert. Extract entities, attributes, and relationships from data.",
                temperature=0.3,
                max_tokens=2000,
            )

            # Parse response to extract primitives
            primitives = self._parse_primitive_response(response)
            return primitives

        except Exception as e:
            print(f"Error extracting primitives with LLM: {e}")
            # Return basic primitives from field analysis as fallback
            return self._extract_primitives_from_fields(field_patterns)

    def _build_primitive_extraction_prompt(
        self, samples: list, field_patterns: dict
    ) -> str:
        """Build prompt for primitive extraction."""
        samples_text = "\n".join(
            [f"Record {i+1}: {sample.text_content[:200]}" for i, sample in enumerate(samples[:5])]
        )

        fields_text = "\n".join(
            [f"- {field}: {info['type']} ({info['non_null_count']} non-null)" for field, info in field_patterns.items()]
        )

        prompt = f"""Analyze the following data samples and extract semantic primitives.

DATA SAMPLES:
{samples_text}

FIELD PATTERNS:
{fields_text}

Extract:
1. **Entities**: Main concepts or objects (e.g., Patient, Treatment, Biomarker)
2. **Attributes**: Properties of entities (e.g., age, name, date)
3. **Relations**: Relationships between entities (e.g., has_treatment, part_of)

Format your response as a list, one per line:
ENTITY: <name> | <evidence> | <confidence>
ATTRIBUTE: <name> | <evidence> | <confidence>
RELATION: <name> | <evidence> | <confidence>

Example:
ENTITY: Patient | Found in patient_id, patient_name fields | 0.95
ATTRIBUTE: age | Numeric field representing patient age | 0.90
RELATION: receives_treatment | Link between patient and treatment | 0.85
"""
        return prompt

    def _parse_primitive_response(self, response: str) -> list[dict]:
        """Parse LLM response to extract structured primitives."""
        primitives = []

        for line in response.strip().split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue

            try:
                type_part, rest = line.split(":", 1)
                prim_type = type_part.strip().lower()

                if prim_type not in ["entity", "attribute", "relation"]:
                    continue

                parts = [p.strip() for p in rest.split("|")]
                if len(parts) >= 2:
                    label = parts[0]
                    evidence = parts[1] if len(parts) > 1 else ""
                    confidence = float(parts[2]) if len(parts) > 2 else 0.8

                    primitives.append(
                        {
                            "label": label,
                            "type": prim_type,
                            "evidence": evidence,
                            "confidence": confidence,
                        }
                    )
            except Exception as e:
                print(f"Error parsing primitive line: {line}, error: {e}")
                continue

        return primitives

    def _extract_primitives_from_fields(self, field_patterns: dict) -> list[dict]:
        """Extract basic primitives from field patterns (fallback)."""
        primitives = []

        # Heuristic: treat fields as attributes
        for field_name, info in field_patterns.items():
            primitives.append(
                {
                    "label": field_name,
                    "type": "attribute",
                    "evidence": f"Field with type {info['type']}",
                    "confidence": 0.7,
                }
            )

        return primitives

    def get_primitives(self, project_id: UUID) -> list[Primitive]:
        """Get all primitives for a project."""
        return self.db.query(Primitive).filter(Primitive.project_id == project_id).all()
