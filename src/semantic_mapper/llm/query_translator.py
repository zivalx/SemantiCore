"""
Query translator.

Translates natural language queries to Cypher.
Translation must be transparent - user sees both the question and generated query.
"""

import json
from typing import Dict, Any, List

from .base import BaseLLMProvider


class QueryTranslationResult:
    """Result of query translation."""

    def __init__(
        self,
        natural_language: str,
        cypher_query: str,
        explanation: str,
        ontology_concepts_used: List[str],
        confidence: float,
        warnings: List[str] = None,
    ):
        self.natural_language = natural_language
        self.cypher_query = cypher_query
        self.explanation = explanation
        self.ontology_concepts_used = ontology_concepts_used
        self.confidence = confidence
        self.warnings = warnings or []


class QueryTranslator:
    """
    Translates natural language queries to Cypher.

    Translation is TRANSPARENT - users see exactly how their question
    maps to the query language.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    def translate(
        self,
        natural_language_query: str,
        ontology_schema: Dict[str, Any],
        sample_instances: Dict[str, List[Dict]] = None,
    ) -> QueryTranslationResult:
        """
        Translate natural language to Cypher.

        Args:
            natural_language_query: User's question
            ontology_schema: Schema context (classes, relationships)
            sample_instances: Sample instances for each class

        Returns:
            QueryTranslationResult with Cypher and explanation
        """
        prompt = self._build_translation_prompt(
            natural_language_query=natural_language_query,
            ontology_schema=ontology_schema,
            sample_instances=sample_instances,
        )

        system_prompt = """You are an expert in translating natural language questions to Cypher queries.

Given a question and an ontology schema, generate a Cypher query that answers the question.

IMPORTANT:
- Use the exact class names and relationship names from the schema
- Instances are stored as nodes with label "Instance"
- Instances have an "INSTANCE_OF" relationship to their OntologyClass
- Instance-to-instance relationships use the "RELATED" relationship with a "type" property
- Explain your query clearly
- If the question is ambiguous, note that in warnings

Respond with JSON in this format:
{{
  "cypher_query": "MATCH ... RETURN ...",
  "explanation": "This query finds... by...",
  "ontology_concepts_used": ["Class1", "RELATIONSHIP_TYPE"],
  "confidence": 0.0-1.0,
  "warnings": ["warning if ambiguous"]
}}"""

        response = self.llm.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more deterministic queries
            max_tokens=2000,
        )

        # Parse response
        result = self._parse_translation_response(
            response_text=response,
            natural_language=natural_language_query,
        )

        return result

    def _build_translation_prompt(
        self,
        natural_language_query: str,
        ontology_schema: Dict[str, Any],
        sample_instances: Dict[str, List[Dict]],
    ) -> str:
        """Build prompt for query translation."""
        # Format schema information
        classes_info = "# Ontology Classes\n"
        for cls in ontology_schema.get("classes", []):
            classes_info += f"\n- **{cls['name']}**: {cls['description']}\n"
            classes_info += f"  Properties: {', '.join([p['name'] for p in cls.get('properties', [])])}\n"

        relationships_info = "\n# Ontology Relationships\n"
        for rel in ontology_schema.get("relationships", []):
            relationships_info += (
                f"\n- **{rel['name']}**: "
                f"({rel['source_class']})-[{rel['name']}]->({rel['target_class']})\n"
            )
            relationships_info += f"  {rel['description']}\n"

        # Format sample instances if available
        samples_info = ""
        if sample_instances:
            samples_info = "\n# Sample Instance Data\n"
            for class_name, instances in sample_instances.items():
                if instances:
                    samples_info += f"\n{class_name} examples:\n"
                    for inst in instances[:2]:  # Show 2 samples
                        samples_info += f"  {json.dumps(inst, indent=2)}\n"

        prompt = f"""{classes_info}
{relationships_info}
{samples_info}

# Query Patterns
Instance nodes: (i:Instance)-[:INSTANCE_OF]->(c:OntologyClass)
Relationships: (source:Instance)-[r:RELATED {{type: "RELATIONSHIP_NAME"}}]->(target:Instance)

# Question
{natural_language_query}

Generate a Cypher query to answer this question."""

        return prompt

    def _parse_translation_response(
        self, response_text: str, natural_language: str
    ) -> QueryTranslationResult:
        """Parse LLM response into QueryTranslationResult."""
        # Extract JSON
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_text = response_text.strip()

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback: try to extract just the query
            return QueryTranslationResult(
                natural_language=natural_language,
                cypher_query=response_text,
                explanation="Failed to parse structured response",
                ontology_concepts_used=[],
                confidence=0.5,
                warnings=["Failed to parse structured response from LLM"],
            )

        return QueryTranslationResult(
            natural_language=natural_language,
            cypher_query=data.get("cypher_query", ""),
            explanation=data.get("explanation", ""),
            ontology_concepts_used=data.get("ontology_concepts_used", []),
            confidence=data.get("confidence", 0.7),
            warnings=data.get("warnings", []),
        )
