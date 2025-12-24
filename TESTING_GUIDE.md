# SemantiCore Testing Guide

This guide walks you through testing the complete Docker-based SemantiCore application with the new React frontend and FastAPI backend.

## Prerequisites

1. **Docker Desktop** must be installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Ensure it's started (look for the Docker icon in your system tray)

2. **Environment Variables** - Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`** with your actual API keys:
   ```bash
   # Required: Add your LLM API key
   ANTHROPIC_API_KEY=your_actual_anthropic_key
   # OR
   OPENAI_API_KEY=your_actual_openai_key

   # Set passwords (or use defaults)
   POSTGRES_PASSWORD=semantic_password
   NEO4J_PASSWORD=semantic_password
   ```

## Quick Start

### 1. Build and Start All Services

```bash
# Build and start all containers (first time may take 5-10 minutes)
docker-compose up --build -d

# View logs to ensure services are starting correctly
docker-compose logs -f
```

Expected output:
- `postgres` - Ready to accept connections
- `neo4j` - Started
- `backend` - Application startup complete
- `frontend` - Ready to serve

### 2. Verify Services Are Running

```bash
# Check service health
docker-compose ps
```

All services should show `Up (healthy)` status:
- `semantic_mapper_postgres` - :5432
- `semantic_mapper_neo4j` - :7474, :7687
- `semantic_mapper_backend` - :8000
- `semantic_mapper_frontend` - :3000

### 3. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: semantic_password)

## Full Wizard Flow Test

Follow these steps to test the complete end-to-end workflow:

### Step 1: Setup Project
1. Navigate to http://localhost:3000
2. Click "Create New Project"
3. Enter project details:
   - **Name**: "Test Product Catalog"
   - **Domain**: "E-commerce"
   - **Description**: "Product catalog with categories, prices, and inventory"
4. Click "Continue"
5. **Expected**: Project created successfully, wizard advances to "Upload Data"

### Step 2: Upload Data
1. Click "Upload Files" button
2. Select test files (CSV, JSON, or text files with product data)
3. **Expected**:
   - Files appear in the upload list
   - Status shows "Uploaded successfully"
   - Backend stores files in `/app/storage/uploads`

### Step 3: Extract Semantic Primitives
1. Click "Extract Primitives" button
2. **Expected**:
   - Job starts (shows progress indicator)
   - Frontend polls backend every 2 seconds
   - After 30-60 seconds, extraction completes
   - Primitives appear in the list (entities, attributes, relationships)
3. **Verify in API**: http://localhost:8000/docs → GET `/api/extraction/primitives/{project_id}`

### Step 4: Generate Ontology
1. Review extracted primitives
2. Click "Generate Ontology" button
3. **Expected**:
   - Job starts (shows progress)
   - LLM generates ontology based on primitives
   - After 60-90 seconds, ontology visualization appears
   - D3.js force-directed graph shows classes and relationships
4. **Verify in Neo4j**:
   - Open http://localhost:7474
   - Run query: `MATCH (o:Ontology) RETURN o`

### Step 5: Review and Accept Ontology
1. Review the generated ontology graph
2. Verify classes, properties, and relationships
3. Click "Accept Ontology" to make it active
4. **Expected**: Ontology marked as accepted in database

### Step 6: Materialize Graph
1. Click "Materialize Knowledge Graph" button
2. **Expected**:
   - Job starts
   - System creates instance nodes in Neo4j
   - Progress shows completion after 30-60 seconds
3. **Verify in Neo4j**:
   - Run query: `MATCH (n) WHERE NOT n:Ontology RETURN count(n)`
   - Should show instance nodes created

### Step 7: Query Data
1. Enter a natural language query, e.g.:
   - "Show all products with price greater than 100"
   - "Find categories with more than 5 products"
2. Click "Execute Query"
3. **Expected**:
   - LLM translates query to Cypher
   - Cypher query executes against Neo4j
   - Results display in table format
4. **Verify Cypher**: Shows generated Cypher query for transparency

### Step 8: Explore Visualization
1. Navigate to "Graph Visualization" tab
2. **Expected**:
   - D3.js visualization of knowledge graph
   - Interactive nodes (drag, zoom, pan)
   - Click nodes to see properties
   - Filter by entity type

## Testing Backend API Directly

### Using FastAPI Docs (Swagger UI)

1. Navigate to http://localhost:8000/docs
2. Test each endpoint:

#### Projects
```
POST /api/projects/
  Body: {"name": "Test", "domain": "Test Domain", "description": "Test"}
  Expected: 201 Created, returns project with ID

GET /api/projects/
  Expected: 200 OK, returns list of projects
```

#### Sources
```
POST /api/sources/upload
  Form Data:
    - project_id: <UUID from above>
    - file: <select a test file>
  Expected: 201 Created, returns source metadata
```

#### Extraction
```
POST /api/extraction/extract?project_id=<UUID>
  Expected: 202 Accepted, returns job_id

GET /api/extraction/primitives/{project_id}
  Expected: 200 OK, returns primitives array (after job completes)
```

#### Jobs
```
GET /api/jobs/{job_id}
  Expected: 200 OK, returns job status (pending → running → completed)
```

### Using cURL

```bash
# Create project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","domain":"Test","description":"Test project"}'

# Get projects
curl http://localhost:8000/api/projects/

# Upload file
curl -X POST http://localhost:8000/api/sources/upload \
  -F "project_id=<UUID>" \
  -F "file=@test_data.csv"

# Start extraction
curl -X POST "http://localhost:8000/api/extraction/extract?project_id=<UUID>"

# Check job status
curl http://localhost:8000/api/jobs/<job_id>
```

## Database Verification

### PostgreSQL

```bash
# Connect to PostgreSQL
docker exec -it semantic_mapper_postgres psql -U postgres -d semantic_mapper

# View projects
SELECT id, name, domain, status, created_at FROM projects;

# View sources
SELECT id, project_id, name, type, file_size FROM sources;

# View jobs
SELECT id, type, status, progress FROM jobs ORDER BY created_at DESC;

# View primitives
SELECT id, label, type, confidence FROM primitives LIMIT 10;

# Exit
\q
```

### Neo4j

1. Open http://localhost:7474
2. Login with: neo4j / semantic_password
3. Run queries:

```cypher
// View all ontologies
MATCH (o:Ontology) RETURN o

// View ontology structure
MATCH (c:Class)-[r]-(p:Property)
WHERE c.ontology_id = '<ONTOLOGY_UUID>'
RETURN c, r, p

// View instances
MATCH (n)
WHERE NOT n:Ontology AND NOT n:Class AND NOT n:Property
RETURN n LIMIT 25

// View graph statistics
CALL apoc.meta.stats()
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
docker-compose logs neo4j

# Restart a specific service
docker-compose restart backend

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Backend Errors

**Database connection failed**
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Check environment variables in `.env`
- View backend logs: `docker-compose logs backend`

**LLM API errors**
- Verify API key is set in `.env`
- Check API key validity
- View backend logs for specific error messages

**File upload fails**
- Check file size (max 50MB by default)
- Ensure storage directory is writable
- Check backend logs

### Frontend Errors

**Can't connect to backend**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check browser console for CORS errors
- Ensure nginx proxy is configured correctly

**API calls timeout**
- LLM operations can take 60-90 seconds
- Check timeout settings in `usePolling` hook
- View backend logs for LLM provider errors

### Database Issues

**PostgreSQL won't start**
```bash
# Remove volume and recreate
docker-compose down -v
docker volume rm semantic_mapper_postgres_data
docker-compose up postgres -d
```

**Neo4j authentication issues**
```bash
# Reset Neo4j password
docker-compose down
docker volume rm semantic_mapper_neo4j_data
docker-compose up neo4j -d
# Wait 30 seconds, then access http://localhost:7474
```

## Performance Benchmarks

Expected timings for typical operations:

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| File upload (10MB CSV) | 2-5 seconds | Depends on network |
| Extract primitives | 30-60 seconds | Depends on file size + LLM |
| Generate ontology | 60-90 seconds | LLM processing time |
| Materialize graph | 30-60 seconds | Depends on data volume |
| Execute query | 5-15 seconds | LLM translation + Neo4j |

## Cleanup

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Success Criteria Checklist

- [ ] All 4 Docker containers start successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API docs accessible at http://localhost:8000/docs
- [ ] Can create a new project
- [ ] Can upload files (CSV, JSON, text)
- [ ] Extraction job completes and primitives appear
- [ ] Ontology generation completes with D3 visualization
- [ ] Can accept ontology and materialize graph
- [ ] Natural language queries translate to Cypher
- [ ] Query results display correctly
- [ ] No console errors in browser
- [ ] No critical errors in backend logs
- [ ] PostgreSQL contains project/job data
- [ ] Neo4j contains ontology and instances

## Next Steps After Testing

1. Test with real production data
2. Adjust LLM prompts for better quality
3. Implement additional query patterns
4. Add graph visualization filters
5. Implement export functionality (CSV, JSON, RDF)
6. Add project sharing/collaboration features
7. Implement auth (if multi-user needed)
8. Set up CI/CD pipeline
9. Deploy to production (AWS, GCP, Azure)
