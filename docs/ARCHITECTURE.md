# Architecture Documentation

This document explains the technical architecture of the SemantiCore platform.

---

## System Overview

```
┌────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │  Upload  │  Define  │  Review  │Materialize│  Query  │ │
│  │   Data   │  Domain  │ Ontology │   Graph   │   Data   │ │
│  └────┬─────┴────┬─────┴────┬─────┴─────┬─────┴────┬─────┘ │
└───────┼──────────┼──────────┼───────────┼──────────┼───────┘
        │          │          │           │          │
        ▼          ▼          ▼           ▼          ▼
┌────────────────────────────────────────────────────────────┐
│                  Application Layer (Python)                 │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │Ingestion │   LLM    │   Graph  │Extraction│  Query   │ │
│  │  Module  │ Provider │   Ops    │  Module  │   Ops    │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘ │
└───────┼──────────┼──────────┼──────────┼──────────┼───────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────┬───────────────────────┬─────────────────┐
│   File System   │    LLM APIs           │     Neo4j       │
│   (Raw Data)    │  (Claude/OpenAI)      │  (Graph DB)     │
└─────────────────┴───────────────────────┴─────────────────┘
```

---

## Core Components

### 1. Models Layer (`models/`)

**Purpose:** Define data structures using Pydantic for validation and serialization.

**Key Models:**

- **Ingestion Models** (`ingestion.py`)
  - `SourceType`: Enum of supported formats
  - `ProvenanceMetadata`: Tracks data lineage
  - `CanonicalRecord`: Normalized data record
  - `IngestionResult`: Result of ingestion operation

- **Primitives** (`primitives.py`)
  - `EntityCandidate`: Proposed entity
  - `RelationshipCandidate`: Proposed relationship
  - `SemanticEvidence`: Evidence linking to source
  - `ConfidenceScore`: Confidence with reasoning

- **Ontology** (`ontology.py`)
  - `OntologyClass`: Class definition
  - `OntologyRelationType`: Relationship definition
  - `Ontology`: Complete ontology
  - `OntologyVersion`: Version tracking
  - `OntologyDiff`: Version differences

- **Proposal** (`proposal.py`)
  - `OntologyProposal`: LLM-generated proposal
  - `ClassProposal`: Proposed class
  - `AlternativeInterpretation`: Alternative designs

- **Feedback** (`feedback.py`)
  - `FeedbackItem`: User feedback
  - `FeedbackSession`: Complete feedback session

---

### 2. Ingestion Layer (`ingestion/`)

**Purpose:** Convert raw data to canonical format.

**Architecture:**

```
┌──────────────────┐
│  IngesterFactory │
└────────┬─────────┘
         │ creates
         ▼
┌──────────────────┐
│  BaseIngester    │ (Abstract)
└────────┬─────────┘
         │ implements
         ▼
┌────────┴────────┬────────┬────────┬────────┐
│  CSVIngester    │  JSON  │  Text  │  PDF   │
└─────────────────┴────────┴────────┴────────┘
```

**Flow:**
1. Factory selects ingester based on file type
2. Ingester reads and normalizes data
3. Returns `IngestionResult` with:
   - `ProvenanceMetadata`
   - List of `CanonicalRecord`
   - Errors and warnings

**Key Principle:** NO semantic interpretation here. Pure data extraction.

---

### 3. Graph Layer (`graph/`)

**Purpose:** Manage Neo4j operations.

**Components:**

- **Neo4jConnection** (`connection.py`)
  - Connection pooling
  - Query execution (read/write)
  - Transaction management

- **OntologyOperations** (`ontology_ops.py`)
  - Create/read ontology in Neo4j
  - Store classes and relationships as nodes
  - Version management
  - Schema initialization

- **InstanceOperations** (`instance_ops.py`)
  - Materialize entity instances
  - Create relationships between instances
  - Link instances to ontology classes
  - Count and query instances

- **QueryOperations** (`query_ops.py`)
  - Execute Cypher queries
  - Get schema context for query translation
  - Validate queries
  - Explain query plans

**Neo4j Graph Structure:**

```cypher
// Ontology layer
(Ontology)-[:DEFINES]->(OntologyClass)
(Ontology)-[:DEFINES]->(OntologyRelationType)
(OntologyClass)-[:CAN_RELATE_VIA]->(OntologyRelationType)
(OntologyRelationType)-[:TARGETS]->(OntologyClass)

// Version tracking
(OntologyVersion)-[:VERSION_OF]->(Ontology)

// Instance layer
(Instance)-[:INSTANCE_OF]->(OntologyClass)
(Instance)-[RELATED {type: "REL_NAME"}]->(Instance)

// Provenance
(Instance)-[:SOURCED_FROM]->(CanonicalRecord)
```

---

### 4. LLM Layer (`llm/`)

**Purpose:** Interface with LLM APIs for proposals and translation.

**Architecture:**

```
┌──────────────┐
│  LLMFactory  │
└──────┬───────┘
       │ creates
       ▼
┌──────────────┐
│BaseLLMProvider│ (Abstract)
└──────┬───────┘
       │ implements
       ▼
┌──────┴──────┬──────────────┐
│  Anthropic  │   OpenAI     │
│  Provider   │   Provider   │
└─────────────┴──────────────┘
       │
       │ used by
       ▼
┌──────────────┬──────────────┐
│  Ontology    │    Query     │
│  Proposer    │  Translator  │
└──────────────┴──────────────┘
```

**Key Classes:**

- **BaseLLMProvider**
  - `generate_structured()`: Returns Pydantic model
  - `generate_text()`: Returns plain text

- **OntologyProposer**
  - Takes domain description + data samples
  - Generates `OntologyProposal`
  - Incorporates feedback from iterations

- **QueryTranslator**
  - Takes natural language question
  - Takes ontology schema context
  - Generates Cypher + explanation

**Important:** All LLM outputs are structured (Pydantic models) or parsed from JSON. No black-box text responses.

---

### 5. Extraction Layer (`extraction/`)

**Purpose:** Analyze canonical records for patterns.

**Note:** This is intentionally minimal. Advanced semantic extraction would require:
- Named Entity Recognition (NER)
- Relationship extraction
- Entity resolution
- Domain-specific rules

For transparency, we keep this simple and let the LLM handle semantic interpretation with human oversight.

---

### 6. UI Layer (`ui/`)

**Purpose:** Streamlit-based interactive interface.

**Pages:**

1. **Main App** (`app.py`)
   - Navigation
   - Status overview
   - Quick links

2. **Upload Data** (`1_upload_data.py`)
   - File upload
   - Format detection
   - Ingestion configuration
   - Record preview

3. **Define Domain** (`2_define_domain.py`)
   - Domain description input
   - Data summary
   - Ontology proposal generation
   - Proposal preview

4. **Review Ontology** (`3_review_ontology.py`)
   - Proposal visualization
   - Feedback collection
   - Accept/modify/reject decision
   - Neo4j storage

5. **Materialize Graph** (`4_materialize_graph.py`)
   - Manual instance creation
   - Instance statistics
   - (Future: automatic materialization)

6. **Query Data** (`5_query_data.py`)
   - Natural language input
   - Query translation
   - Cypher generation
   - Result display

7. **Settings** (`6_settings.py`)
   - Configuration
   - Connection testing
   - Data management

**Session State:**

```python
st.session_state = {
    "ingested_sources": [],       # List of DataSource
    "canonical_records": [],       # List of CanonicalRecord
    "domain_description": "",      # User's domain text
    "current_proposal": None,      # OntologyProposal
    "accepted_ontology": None,     # Accepted Ontology + metadata
    "previous_feedback": "",       # Feedback for next iteration
}
```

---

## Data Flow

### Complete Workflow

```
1. INGESTION
   User uploads CSV
        ↓
   CSVIngester.ingest()
        ↓
   CanonicalRecord[] + ProvenanceMetadata
        ↓
   Store in session_state

2. PROPOSAL
   User describes domain
        ↓
   SemanticExtractor.get_sample_records()
        ↓
   OntologyProposer.propose_ontology()
        ↓
   LLM API call with structured output
        ↓
   OntologyProposal
        ↓
   Store in session_state

3. FEEDBACK
   User reviews proposal
        ↓
   User provides feedback
        ↓
   FeedbackSession created
        ↓
   IF accept:
       Convert to Ontology
       OntologyOperations.create_ontology()
       Store in Neo4j
   ELSE:
       Store feedback
       Go back to step 2

4. MATERIALIZATION
   User creates instances manually
        ↓
   InstanceOperations.materialize_entity()
        ↓
   Instance nodes in Neo4j
   Linked to OntologyClass

5. QUERYING
   User asks question in NL
        ↓
   QueryOperations.get_ontology_schema_context()
        ↓
   QueryTranslator.translate()
        ↓
   LLM API call
        ↓
   Cypher query + explanation
        ↓
   QueryOperations.execute_cypher()
        ↓
   Results displayed
```

---

## Design Patterns

### 1. Factory Pattern
- `IngesterFactory`: Creates appropriate ingester
- `LLMFactory`: Creates appropriate LLM provider

### 2. Strategy Pattern
- `BaseIngester`: Different ingestion strategies
- `BaseLLMProvider`: Different LLM providers

### 3. Repository Pattern
- `OntologyOperations`: Ontology CRUD operations
- `InstanceOperations`: Instance CRUD operations

### 4. Value Objects
- `ConfidenceScore`: Immutable confidence representation
- `ProvenanceMetadata`: Immutable provenance tracking

---

## Error Handling

### Levels of Error Handling

1. **Validation Errors** (Pydantic)
   - Caught at model instantiation
   - User sees clear validation messages

2. **Ingestion Errors**
   - File not found
   - Invalid format
   - Returned in `IngestionResult.errors`

3. **Database Errors**
   - Connection failures
   - Query errors
   - Caught and displayed with context

4. **LLM Errors**
   - API failures
   - Invalid JSON responses
   - Caught with retry logic (future)

---

## Security Considerations

### Current State

- ✅ Pydantic validation prevents injection
- ✅ Neo4j parameterized queries prevent Cypher injection
- ✅ API keys in environment variables
- ❌ No authentication (single-user)
- ❌ No authorization (local only)
- ❌ No encryption (local database)

### Production Recommendations

1. Add user authentication
2. Implement role-based access control
3. Encrypt sensitive data in Neo4j
4. Use HTTPS for all connections
5. Audit logging for all changes
6. Rate limiting on LLM calls

---

## Performance Considerations

### Current Bottlenecks

1. **LLM API calls** (30-60 seconds)
   - Solution: Caching, streaming responses

2. **Large file ingestion**
   - Solution: Streaming ingestion, progress bars

3. **Complex graph queries**
   - Solution: Indexing, query optimization

### Scaling Strategies

1. **Horizontal scaling** — Multiple workers for ingestion
2. **Caching** — Cache LLM responses for similar queries
3. **Async processing** — Background jobs for long operations
4. **Database sharding** — Separate ontologies in different graphs

---

## Testing Strategy

### Unit Tests
- Model validation
- Ingester logic
- Graph operations

### Integration Tests
- End-to-end ingestion
- Ontology creation in Neo4j
- Query execution

### UI Tests
- Streamlit component testing
- Session state management

---

## Future Architecture Enhancements

1. **Background Job Queue**
   - Celery for async tasks
   - Long-running ingestion
   - Batch materialization

2. **Caching Layer**
   - Redis for LLM response cache
   - Query result cache

3. **Event Sourcing**
   - All changes as events
   - Full audit trail
   - Replay capability

4. **API Layer**
   - REST API for programmatic access
   - WebSocket for real-time updates

5. **Microservices**
   - Separate ingestion service
   - Separate LLM service
   - Separate query service

---

## Conclusion

The architecture prioritizes:
- **Transparency** — Every step is visible
- **Modularity** — Components are independent
- **Extensibility** — Easy to add new formats, LLMs, etc.
- **Simplicity** — No over-engineering

This is a foundation for serious semantic systems, not a toy demo.
