# Semantic Mapper

**An Ontology-First Semantic Graph Platform**

Transform heterogeneous raw data into queryable semantic graphs through a transparent, human-in-the-loop ontology design process.

---

## Philosophy

This is **not** a toy demo. This is a serious showcase of how semantic systems should be built:

### Core Principles

1. **Ontology is a first-class artifact** — not an afterthought
   - Stored explicitly in Neo4j as a graph structure
   - Versioned and traceable
   - Independent of instance data

2. **Explicit uncertainty** — the system represents what it doesn't know
   - Confidence scores with reasoning
   - Alternative interpretations
   - Open questions for human input

3. **LLMs propose, humans decide** — AI assists, humans control
   - Every ontology element is reviewed
   - Feedback shapes iterations
   - No black-box automation

4. **Full traceability** — every decision has provenance
   - Semantic elements link to source data
   - Ontology changes are versioned
   - Query translations are visible

5. **Transparency beats automation** — clarity over magic
   - See the generated Cypher
   - Understand confidence scores
   - Review LLM reasoning

---

## What This System Does

```
┌─────────────┐
│ Raw Data    │ CSV, JSON, Text, PDF, DOCX
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Canonical   │ Normalized intermediate format
│ Records     │ (Provenance preserved)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Domain      │ Human describes the domain
│ Description │ in natural language
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Ontology    │ LLM proposes classes & relationships
│ Proposal    │ (with explanations, confidence, alternatives)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Human       │ Accept / Modify / Request revision
│ Feedback    │ Iterate until satisfied
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Accepted    │ Ontology stored in Neo4j
│ Ontology    │ (versioned, traceable)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Instance    │ Data materialized as graph
│ Graph       │ according to ontology
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Natural     │ Ask questions, get Cypher,
│ Language    │ see results (transparently)
│ Queries     │
└─────────────┘
```

---

## Architecture

### Tech Stack

- **Python 3.11** — Modern Python with type hints
- **Neo4j Community Edition** — Graph database (local)
- **Streamlit** — Interactive UI
- **Pydantic** — Data validation and serialization
- **Neo4j Python Driver** — Official driver
- **LLM APIs** — Claude (Anthropic) or GPT-4 (OpenAI)

### Project Structure

```
semantic_mapper/
├── src/semantic_mapper/
│   ├── models/              # Pydantic data models
│   │   ├── primitives.py    # Semantic candidates
│   │   ├── ontology.py      # Ontology structures
│   │   ├── ingestion.py     # Data ingestion models
│   │   ├── proposal.py      # LLM proposals
│   │   └── feedback.py      # Human feedback
│   │
│   ├── ingestion/           # Data ingesters
│   │   ├── csv_ingester.py
│   │   ├── json_ingester.py
│   │   ├── text_ingester.py
│   │   ├── pdf_ingester.py
│   │   └── docx_ingester.py
│   │
│   ├── graph/               # Neo4j operations
│   │   ├── connection.py    # Connection management
│   │   ├── ontology_ops.py  # Ontology CRUD
│   │   ├── instance_ops.py  # Instance materialization
│   │   └── query_ops.py     # Query execution
│   │
│   ├── llm/                 # LLM integration
│   │   ├── anthropic_provider.py
│   │   ├── openai_provider.py
│   │   ├── ontology_proposer.py
│   │   └── query_translator.py
│   │
│   ├── extraction/          # Semantic extraction
│   │   └── extractor.py     # Analysis utilities
│   │
│   └── ui/                  # Streamlit UI
│       ├── app.py           # Main app
│       └── pages/           # UI pages
│           ├── 1_upload_data.py
│           ├── 2_define_domain.py
│           ├── 3_review_ontology.py
│           ├── 4_materialize_graph.py
│           ├── 5_query_data.py
│           └── 6_settings.py
│
├── data/
│   ├── raw/                 # Raw data files
│   └── examples/            # Example datasets
│
├── docs/                    # Documentation
├── tests/                   # Tests
└── config/                  # Configuration files
```

---

## Installation

### Prerequisites

1. **Python 3.11+**
2. **Neo4j Community Edition** (local instance)
3. **API Keys** (Anthropic or OpenAI)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd semantic_mapper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# - Neo4j credentials
# - LLM API keys
```

### Configure Neo4j

1. Install Neo4j Desktop or Community Edition
2. Create a new database
3. Start the database
4. Note the connection details (default: bolt://localhost:7687)
5. Update `.env` with credentials

### Configure LLM

Choose **Anthropic** (recommended) or **OpenAI**:

```bash
# For Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OR for OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

---

## Quick Start

### Three Ways to Run

**1. Easy Start (Recommended)**
```bash
# Unix/Mac/Linux
./scripts/start.sh

# Windows
scripts\start.bat
```

**2. Docker**
```bash
docker-compose up -d
```
Access at http://localhost:8501

**3. Manual**
```bash
streamlit run src/semantic_mapper/ui/app.py
```

### 5-Minute Example

```bash
# 1. Start the app (use one of the methods above)
# 2. Upload data/examples/ecommerce_orders.csv
# 3. Describe domain: "E-commerce orders with customers and products"
# 4. Generate ontology proposal (wait 30-60 sec)
# 5. Review and accept
# 6. Create sample instances
# 7. Query: "How many orders are there?"
```

---

## Documentation

- **[Quick Start](docs/QUICK_START.md)** — Get running in 10 minutes
- **[Usage Guide](docs/USAGE_GUIDE.md)** — Comprehensive examples for every feature
- **[Deployment Guide](docs/DEPLOYMENT.md)** — Local, Docker, and cloud deployment
- **[Architecture](docs/ARCHITECTURE.md)** — Technical deep dive
- **[Contributing](CONTRIBUTING.md)** — Development guidelines and standards

---

## Basic Workflow

#### 1. Upload Data

- Navigate to **Upload Data**
- Upload CSV, JSON, text, PDF, or DOCX files
- Data is converted to canonical format
- No semantic interpretation yet

#### 2. Define Domain

- Navigate to **Define Domain**
- Describe your domain in natural language
- Example:

  ```
  This data represents an e-commerce system with customers,
  orders, and products. Customers place orders containing
  multiple items. Products belong to categories.
  ```

- Click **Generate Proposal**
- Wait 30-60 seconds for LLM to analyze and propose

#### 3. Review Ontology

- Navigate to **Review Ontology**
- Examine proposed classes and relationships
- Review confidence scores and explanations
- **Options:**
  - ✅ **Accept** — Save to Neo4j and proceed
  - ✏️ **Request Modifications** — Provide feedback for next iteration
  - 🔄 **Request New Proposal** — Start over with guidance

#### 4. Materialize Graph (Manual)

- Navigate to **Materialize Graph**
- Create sample instances of ontology classes
- In production, this would use LLM for automatic mapping

#### 5. Query Data

- Navigate to **Query Data**
- **Natural Language Mode:**
  - Ask questions in plain English
  - See the generated Cypher query
  - Review explanation and concepts used
  - Execute and see results
- **Direct Cypher Mode:**
  - Write Cypher directly
  - Execute and see results

---

## Ontology Storage in Neo4j

The ontology itself is stored as a graph:

```cypher
// Ontology structure
(Ontology)-[:DEFINES]->(OntologyClass)
(Ontology)-[:DEFINES]->(OntologyRelationType)

(OntologyClass)-[:CAN_RELATE_VIA]->(OntologyRelationType)
(OntologyRelationType)-[:TARGETS]->(OntologyClass)

// Instances
(Instance)-[:INSTANCE_OF]->(OntologyClass)
(Instance)-[RELATED {type: "REL_NAME"}]->(Instance)
```

This allows:
- Querying the ontology itself
- Versioning and tracking changes
- Storing rejected alternatives
- Full provenance

---

## Key Features

### ✅ Implemented

- ✅ Multi-format data ingestion (CSV, JSON, text, PDF, DOCX)
- ✅ Canonical normalization with provenance
- ✅ LLM-based ontology proposal
- ✅ Confidence scores with reasoning
- ✅ Human-in-the-loop feedback
- ✅ Ontology storage in Neo4j
- ✅ Ontology versioning
- ✅ Natural language query translation
- ✅ Transparent Cypher generation
- ✅ Interactive Streamlit UI

### 🚧 Intentionally Simplified

These are **not** missing features — they're deliberately simplified to maintain transparency:

- **Automatic instance materialization** — Requires complex LLM-based mapping
- **Relationship extraction** — Needs NLP and entity resolution
- **Conflict resolution** — Human decisions needed
- **Entity deduplication** — Domain-specific logic required

### 🔮 Future Enhancements

- Visual ontology graph editor
- Ontology diff viewer
- Batch instance import with LLM mapping
- Query result visualization
- Export to OWL/RDF
- Multi-user collaboration

---

## Design Decisions & Limitations

### What This System IS

- ✅ A platform for **ontology-first** semantic modeling
- ✅ A **human-in-the-loop** system for data transformation
- ✅ A **transparent** alternative to black-box knowledge graphs
- ✅ A **production-quality scaffold** ready for extension

### What This System IS NOT

- ❌ A fully automated knowledge graph builder
- ❌ An entity resolution system
- ❌ A pre-built domain ontology (you create your own)
- ❌ A replacement for human domain expertise

### Key Limitations

1. **Manual instance creation** — Automatic mapping requires domain-specific rules
2. **Single-user** — No collaboration features yet
3. **English only** — LLM prompts are in English

### Why These Limitations?

Because **transparency beats automation**. It's better to show what the system *can't* do than to hide it behind automation and pretend everything works.

---

## Examples

See `data/examples/` for:

1. **E-commerce dataset** (CSV) — Orders, customers, products
2. **Research papers** (PDF) — Academic paper metadata
3. **JSON API responses** — Nested data structures
4. **Ontology evolution** — v1 → v2 with feedback

---

## Development

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format
black src/

# Lint
ruff src/

# Type check
mypy src/
```

---

## Philosophy Deep Dive

### Why Ontology-First?

Most data systems treat ontology as an afterthought:
1. Build the database
2. Write queries
3. Maybe document the schema later

This system inverts that:
1. **Define ontology** (with human oversight)
2. **Map data** to ontology
3. **Query semantically** (not just syntactically)

### Why Human-in-the-Loop?

LLMs are powerful but not infallible. For serious systems:
- Humans understand **domain context**
- Humans make **strategic decisions**
- Humans accept **responsibility**

LLMs should **assist**, not **replace**.

### Why Transparency?

"AI-powered" often means "black box." This system shows:
- **How** decisions are made
- **Why** with confidence scores
- **What** alternatives exist

You can trust what you can inspect.

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

**Areas for improvement:**
- Additional data formats (Excel, XML, SQL dumps)
- Better visualization (graph rendering, ontology diagrams)
- Advanced query features (aggregations, graph algorithms)
- Entity resolution and deduplication
- Automatic relationship extraction
- Multi-language support

**Development setup:**
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code quality
black src/ && ruff src/ && mypy src/
```

---

## License

MIT License — See LICENSE file

---

## Acknowledgments

Built on the shoulders of giants:
- Neo4j for graph database
- Anthropic/OpenAI for LLMs
- Pydantic for data validation
- Streamlit for rapid UI development

---

## Contact

Questions? Ideas? Open an issue or discussion!

**Remember:** This system helps humans formalize meaning. It doesn't pretend to "understand" your domain — that's your job. It just makes the process explicit, traceable, and iterative.
