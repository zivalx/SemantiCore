# SemantiCore

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

### Two UI Options

This project provides **two complete UI implementations**:

#### 1. **Streamlit UI** (Simple, All-in-One)
- Single-page app with wizard workflow
- Perfect for local development and demos
- Branded as "SemantiCore" in the interface
- Connects directly to Neo4j

#### 2. **React + FastAPI** (Production-Ready)
- Modern TypeScript frontend with Vite
- RESTful API backend with FastAPI
- PostgreSQL for application state + Neo4j for knowledge graph
- Docker Compose orchestration
- Scalable and production-ready

### Tech Stack

**Core:**
- **Python 3.11** — Modern Python with type hints
- **Neo4j Community Edition 5.15** — Knowledge graph storage
- **Pydantic** — Data validation and serialization
- **LLM APIs** — Claude (Anthropic) or GPT-4 (OpenAI)

**Streamlit UI:**
- **Streamlit** — Interactive Python UI
- Direct Neo4j connection

**React + API Stack:**
- **FastAPI** — High-performance Python REST API
- **PostgreSQL 15** — Application state (projects, jobs, sources)
- **React 19** — Modern UI framework
- **TypeScript 5** — Type-safe frontend
- **Vite** — Fast build tooling
- **D3.js** — Graph visualizations
- **Docker Compose** — Multi-service orchestration

### Project Structure

```
semantic_mapper/
├── src/semantic_mapper/          # Core Python package
│   ├── models/                   # Pydantic data models
│   │   ├── primitives.py         # Semantic candidates
│   │   ├── ontology.py           # Ontology structures
│   │   ├── ingestion.py          # Data ingestion models
│   │   ├── proposal.py           # LLM proposals
│   │   └── feedback.py           # Human feedback
│   │
│   ├── ingestion/                # Data ingesters
│   │   ├── csv_ingester.py       # CSV data ingestion
│   │   ├── json_ingester.py      # JSON data ingestion
│   │   ├── text_ingester.py      # Plain text ingestion
│   │   ├── pdf_ingester.py       # PDF document ingestion
│   │   └── docx_ingester.py      # DOCX document ingestion
│   │
│   ├── graph/                    # Neo4j operations
│   │   ├── connection.py         # Connection management
│   │   ├── ontology_ops.py       # Ontology CRUD
│   │   ├── instance_ops.py       # Instance materialization
│   │   └── query_ops.py          # Query execution
│   │
│   ├── llm/                      # LLM integration
│   │   ├── anthropic_provider.py # Claude integration
│   │   ├── openai_provider.py    # GPT integration
│   │   ├── factory.py            # Provider factory
│   │   ├── ontology_proposer.py  # Ontology generation
│   │   └── query_translator.py   # NL → Cypher translation
│   │
│   ├── extraction/               # Semantic extraction
│   │   └── extractor.py          # Primitive extraction
│   │
│   └── ui/                       # Streamlit UI
│       ├── app.py                # Main SemantiCore app
│       └── pages/                # UI pages
│           ├── query.py          # Query interface
│           └── settings.py       # Settings page
│
├── backend/                      # FastAPI backend (optional)
│   ├── api/
│   │   ├── main.py               # FastAPI application
│   │   ├── dependencies.py       # Shared dependencies
│   │   ├── routers/              # API endpoints
│   │   │   ├── projects.py       # Project management
│   │   │   ├── sources.py        # Data source management
│   │   │   ├── jobs.py           # Background job tracking
│   │   │   ├── extraction.py     # Semantic extraction API
│   │   │   ├── ontology.py       # Ontology operations
│   │   │   ├── materialization.py # Graph materialization
│   │   │   └── query.py          # Query execution
│   │   └── models/               # Request/response models
│   ├── db/                       # PostgreSQL database
│   │   ├── connection.py         # DB connection
│   │   └── models.py             # SQLAlchemy models
│   ├── services/                 # Business logic
│   │   ├── extraction_service.py
│   │   ├── ontology_service.py
│   │   ├── materialization_service.py
│   │   └── query_service.py
│   ├── config.py                 # Configuration
│   ├── Dockerfile                # Backend container
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # React frontend (optional)
│   ├── src/
│   │   ├── App.tsx               # Main React app
│   │   ├── components/           # React components
│   │   ├── types.ts              # TypeScript types
│   │   └── constants.tsx         # App constants
│   ├── Dockerfile                # Frontend container
│   ├── nginx.conf                # Nginx configuration
│   ├── package.json              # Node dependencies
│   └── vite.config.ts            # Vite configuration
│
├── data/
│   ├── raw/                      # Raw data files
│   └── examples/                 # Example datasets
│
├── docs/                         # Documentation
│   ├── QUICK_START.md
│   ├── USAGE_GUIDE.md
│   ├── DEPLOYMENT.md
│   └── ARCHITECTURE.md
│
├── tests/                        # Tests
├── docker-compose.yml            # Full-stack orchestration
├── .env.example                  # Environment template
└── README.md
```

### Database Architecture

**Dual-Database Design:**

1. **PostgreSQL** (Application State)
   - Projects, jobs, data sources
   - User workflow tracking
   - Background job status
   - Used by: FastAPI backend

2. **Neo4j** (Knowledge Graph)
   - Ontology schema (classes, relationships)
   - Instance data (entities, relations)
   - Ontology versioning
   - Query execution
   - Used by: Both Streamlit and FastAPI

---

## Installation

### Prerequisites

**For Streamlit UI:**
- Python 3.11+
- Neo4j Community Edition 5.15+
- API Keys (Anthropic or OpenAI)

**For React + API:**
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- PostgreSQL 15+
- Neo4j Community Edition 5.15+
- API Keys (Anthropic or OpenAI)

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

# Edit .env with your settings:
# - Database credentials
# - LLM API keys
nano .env  # or use your favorite editor
```

### Configure Databases

#### Neo4j (Required for both UIs)

**Option 1: Docker (Recommended)**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5.15-community
```

**Option 2: Neo4j Desktop**
1. Install Neo4j Desktop
2. Create a new database
3. Start the database
4. Note connection details (default: bolt://localhost:7687)

#### PostgreSQL (Only for React + API)

**Option 1: Docker (Recommended)**
```bash
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=semantic_mapper \
  postgres:15-alpine
```

**Option 2: Local Installation**
- Install PostgreSQL 15+
- Create database: `createdb semantic_mapper`

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

### Option 1: Streamlit UI (Simplest)

Perfect for local development, demos, and single-user scenarios.

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run Streamlit app
streamlit run src/semantic_mapper/ui/app.py
```

**Access:** http://localhost:8501

**Features:**
- SemantiCore branded interface
- Full wizard workflow (8 steps)
- Project management
- Direct Neo4j integration
- Query interface with natural language → Cypher translation

### Option 2: React + FastAPI (Production)

Full-stack architecture with REST API, React frontend, and dual databases.

**Using Docker Compose (Recommended):**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- PostgreSQL: localhost:5432

**Manual Setup (Development):**
```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev

# Terminal 3: Ensure databases are running
# Neo4j on port 7687
# PostgreSQL on port 5432
```

---

## Usage Workflows

### Streamlit Workflow

1. **Open App** → http://localhost:8501
2. **Hub Overview** → View existing projects
3. **New Deployment** → Start wizard:
   - **Step 1: Identity** → Project name
   - **Step 2: Frame** → Domain description
   - **Step 3: Ingest** → Upload data files
   - **Step 4: Extract** → Review primitives
   - **Step 5: Propose** → Review ontology
   - **Step 6: Negotiate** → Commit blueprint
   - **Step 7: Knowledge** → Visualize graph
   - **Step 8: Query** → Query with natural language

4. **Query Interface** → Natural language or Cypher queries
5. **Settings** → Configure LLM and Neo4j

### React + API Workflow

1. **Open App** → http://localhost:3000
2. **Create Project** → Define project and domain
3. **Upload Data** → Add CSV, JSON, text, PDF, or DOCX files
4. **Extract Primitives** → AI extracts semantic elements
5. **Review Ontology** → Accept, modify, or request revisions
6. **Materialize Graph** → Create instances in Neo4j
7. **Query Data** → Natural language or Cypher queries
8. **API Access** → Use REST API at http://localhost:8000/docs

---

## API Documentation

The FastAPI backend provides comprehensive REST endpoints:

### Projects
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `DELETE /api/projects/{id}` - Delete project

### Data Sources
- `POST /api/sources` - Upload data source
- `GET /api/sources` - List sources for project
- `GET /api/sources/{id}` - Get source details

### Extraction
- `POST /api/extraction/extract` - Extract semantic primitives
- `GET /api/extraction/results/{job_id}` - Get extraction results

### Ontology
- `POST /api/ontology/propose` - Generate ontology proposal
- `GET /api/ontology/{id}` - Get ontology details
- `POST /api/ontology/{id}/feedback` - Submit human feedback
- `PUT /api/ontology/{id}/accept` - Accept and store ontology

### Materialization
- `POST /api/materialization/materialize` - Create graph instances
- `GET /api/materialization/status/{job_id}` - Check job status

### Query
- `POST /api/query/translate` - Translate NL to Cypher
- `POST /api/query/execute` - Execute Cypher query
- `GET /api/query/schema/{ontology_id}` - Get ontology schema

**Full API Documentation:** http://localhost:8000/docs (when backend is running)

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
- ✅ Two complete UI implementations (Streamlit + React)
- ✅ RESTful API with FastAPI
- ✅ Dual-database architecture (PostgreSQL + Neo4j)
- ✅ Docker Compose orchestration

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
- Advanced graph algorithms

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
2. **English only** — LLM prompts are in English
3. **Single-user Streamlit** — No collaboration features in Streamlit UI
4. **React UI in development** — Full feature parity still being developed

### Why These Limitations?

Because **transparency beats automation**. It's better to show what the system *can't* do than to hide it behind automation and pretend everything works.

---

## Examples

See `data/examples/` for:

1. **E-commerce dataset** (CSV) — Orders, customers, products
2. **Research papers** (JSON) — Paper metadata and citations
3. **Clinical trials** (PDF) — Trial eligibility criteria
4. **Product events** (JSON) — Usage analytics events

---

## Development

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format
black src/ backend/

# Lint
ruff check src/ backend/

# Type check
mypy src/ backend/
```

### Frontend Development

```bash
cd frontend
npm run dev       # Development server
npm run build     # Production build
npm run preview   # Preview production build
```

---

## Deployment

### Streamlit (Simple)

**Railway:**
```bash
railway up
```

**Render:**
- Connect GitHub repository
- Set build command: `pip install -e .`
- Set start command: `streamlit run src/semantic_mapper/ui/app.py`

### React + API (Production)

**Docker Compose (Any Platform):**
```bash
docker-compose up -d
```

**Kubernetes:**
See `docs/DEPLOYMENT.md` for Kubernetes manifests.

**Cloud Platforms:**
- AWS ECS with RDS and Managed Neo4j
- Google Cloud Run with Cloud SQL and Neo4j Aura
- Azure Container Instances with Azure Database

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

### Why Two UIs?

- **Streamlit:** Quick prototyping, demos, single-user workflows
- **React + API:** Production deployments, multi-user, integrations

Choose the right tool for your use case!

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
- React UI feature completion

**Development setup:**
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Frontend dev dependencies
cd frontend && npm install

# Run tests
pytest tests/

# Code quality
black src/ backend/ && ruff src/ backend/ && mypy src/ backend/
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
- Streamlit for rapid prototyping
- FastAPI for high-performance APIs
- React for modern UI development

---

## Contact

Questions? Ideas? Open an issue or discussion!

**Remember:** This system helps humans formalize meaning. It doesn't pretend to "understand" your domain — that's your job. It just makes the process explicit, traceable, and iterative.
