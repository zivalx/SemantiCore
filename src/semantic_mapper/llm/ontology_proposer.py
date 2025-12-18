"""
Ontology proposer.

Uses LLM to generate ontology proposals from canonical data and domain description.
LLMs propose — humans decide.
"""

import json
from typing import List, Optional
from uuid import UUID

from .base import BaseLLMProvider
from ..models.ingestion import CanonicalRecord, DataSource
from ..models.ontology import OntologyClass, OntologyRelationType, DataType
from ..models.proposal import (
    OntologyProposal,
    ClassProposal,
    RelationProposal,
    AlternativeInterpretation,
)
from ..models.primitives import ConfidenceScore


class OntologyProposer:
    """
    Generates ontology proposals using an LLM.

    This component transforms data samples and domain knowledge into
    structured ontology proposals that humans can review and refine.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    def propose_ontology(
        self,
        domain_description: str,
        data_samples: List[CanonicalRecord],
        source_ids: List[UUID],
        iteration: int = 1,
        previous_feedback: Optional[str] = None,
    ) -> OntologyProposal:
        """
        Generate an ontology proposal.

        Args:
            domain_description: Free-text description of the domain
            data_samples: Sample canonical records
            source_ids: IDs of data sources
            iteration: Iteration number (for refinement)
            previous_feedback: Feedback from previous iteration

        Returns:
            OntologyProposal with classes and relationships
        """
        # Build prompt
        prompt = self._build_proposal_prompt(
            domain_description=domain_description,
            data_samples=data_samples,
            iteration=iteration,
            previous_feedback=previous_feedback,
        )

        system_prompt = """You are an expert ontology engineer and semantic modeler.

Your task is to propose a formal ontology (classes and relationships) based on:
1. A domain description provided by a human
2. Sample data records

CRITICAL PRINCIPLES:
- Be explicit about uncertainty - if you're unsure, say so
- Offer alternative interpretations when multiple approaches are valid
- Every decision must have clear rationale
- Properties should have appropriate data types
- Focus on SEMANTIC meaning, not just field names
- Classes represent concepts, not database tables
- Relationships represent meaningful connections

You will respond with a structured ontology proposal in JSON format."""

        # For now, we'll use generate_text and parse manually
        # In production, you'd use a structured output approach
        response_text = self.llm.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000,
        )

        # Parse response (this is a simplified version)
        # In production, you'd want more robust parsing with structured output
        proposal = self._parse_proposal_response(
            response_text=response_text,
            source_ids=source_ids,
        )

        return proposal

    def _build_proposal_prompt(
        self,
        domain_description: str,
        data_samples: List[CanonicalRecord],
        iteration: int,
        previous_feedback: Optional[str],
    ) -> str:
        """Build the prompt for ontology proposal."""
        # Sample records for context
        sample_text = ""
        for idx, record in enumerate(data_samples[:10]):  # Limit to 10 samples
            sample_text += f"\n\nSample {idx + 1}:\n"
            sample_text += json.dumps(record.structured_fields, indent=2)

        prompt = f"""# Domain Description
{domain_description}

# Sample Data Records
{sample_text}

# Task
{"This is iteration " + str(iteration) + " of the ontology design." if iteration > 1 else ""}
{f"Previous feedback: {previous_feedback}" if previous_feedback else ""}

Please propose an ontology that captures the semantic structure of this domain.

Provide your proposal in the following JSON format:
{{
  "ontology_name": "string",
  "domain_description": "string",
  "overall_explanation": "string explaining your overall modeling approach",
  "classes": [
    {{
      "name": "ClassName",
      "label": "Human Readable Label",
      "description": "What this class represents",
      "properties": [
        {{
          "name": "propertyName",
          "data_type": "string|integer|float|boolean|date|datetime|uri|json",
          "description": "What this property means",
          "is_required": true/false
        }}
      ],
      "examples": ["example instance 1", "example instance 2"],
      "rationale": "Why this class exists",
      "confidence": {{
        "score": 0.0-1.0,
        "reasoning": "Why this confidence level"
      }},
      "open_questions": ["question 1", "question 2"],
      "alternatives": [
        {{
          "description": "Alternative way to model this",
          "rationale": "Why this might be better",
          "tradeoffs": {{
            "pros": "advantages",
            "cons": "disadvantages"
          }}
        }}
      ]
    }}
  ],
  "relationships": [
    {{
      "name": "RELATIONSHIP_NAME",
      "label": "Human Readable Label",
      "description": "What this relationship means",
      "source_class": "SourceClassName",
      "target_class": "TargetClassName",
      "cardinality": "one-to-one|one-to-many|many-to-one|many-to-many",
      "examples": ["example relationship"],
      "rationale": "Why this relationship exists",
      "confidence": {{
        "score": 0.0-1.0,
        "reasoning": "Why this confidence level"
      }},
      "alternatives": [...]
    }}
  ],
  "assumptions": ["assumption 1", "assumption 2"],
  "open_questions": ["question 1", "question 2"]
}}

Be thorough but pragmatic. Focus on the most important semantic structures."""

        return prompt

    def _parse_proposal_response(
        self, response_text: str, source_ids: List[UUID]
    ) -> OntologyProposal:
        """Parse LLM response into OntologyProposal."""
        # Extract JSON from response
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_text = response_text.strip()

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        # Build class proposals
        class_proposals = []
        for cls_data in data.get("classes", []):
            ont_class = OntologyClass(
                name=cls_data["name"],
                label=cls_data.get("label", cls_data["name"]),
                description=cls_data["description"],
                properties=[],  # Simplified for now
                examples=cls_data.get("examples", []),
                rationale=cls_data.get("rationale", ""),
            )

            confidence = ConfidenceScore(
                score=cls_data.get("confidence", {}).get("score", 0.7),
                reasoning=cls_data.get("confidence", {}).get("reasoning", "LLM generated"),
            )

            class_proposal = ClassProposal(
                proposed_class=ont_class,
                plain_english_explanation=cls_data["description"],
                confidence=confidence,
                open_questions=cls_data.get("open_questions", []),
                alternatives=[],  # Simplified for now
            )
            class_proposals.append(class_proposal)

        # Build relation proposals
        relation_proposals = []
        for rel_data in data.get("relationships", []):
            ont_rel = OntologyRelationType(
                name=rel_data["name"],
                label=rel_data.get("label", rel_data["name"]),
                description=rel_data["description"],
                source_class=rel_data["source_class"],
                target_class=rel_data["target_class"],
                cardinality=rel_data.get("cardinality", "many-to-many"),
                examples=rel_data.get("examples", []),
                rationale=rel_data.get("rationale", ""),
            )

            confidence = ConfidenceScore(
                score=rel_data.get("confidence", {}).get("score", 0.7),
                reasoning=rel_data.get("confidence", {}).get("reasoning", "LLM generated"),
            )

            relation_proposal = RelationProposal(
                proposed_relation=ont_rel,
                plain_english_explanation=rel_data["description"],
                confidence=confidence,
                open_questions=rel_data.get("open_questions", []),
                alternatives=[],
            )
            relation_proposals.append(relation_proposal)

        # Build overall proposal
        overall_confidence = ConfidenceScore(
            score=0.75,  # Placeholder
            reasoning="Generated from LLM analysis of domain and data",
        )

        proposal = OntologyProposal(
            ontology_name=data.get("ontology_name", "Proposed Ontology"),
            domain_description=data.get("domain_description", ""),
            class_proposals=class_proposals,
            relation_proposals=relation_proposals,
            overall_explanation=data.get("overall_explanation", ""),
            assumptions=data.get("assumptions", []),
            open_questions=data.get("open_questions", []),
            confidence=overall_confidence,
            based_on_source_ids=source_ids,
        )

        return proposal
