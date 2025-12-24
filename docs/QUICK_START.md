# Quick Start Guide

Get up and running with SemantiCore in 10 minutes.

---

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] Neo4j installed (Desktop or Community Edition)
- [ ] API key for Anthropic (Claude) or OpenAI (GPT-4)

---

## Step 1: Install Neo4j

### Option A: Neo4j Desktop (Recommended)

1. Download from https://neo4j.com/download/
2. Install and create a new project
3. Create a new database (name it "semanticore")
4. Set password (remember this!)
5. Start the database
6. Note the connection URI (usually `bolt://localhost:7687`)

### Option B: Docker

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

---

## Step 2: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd semantic_mapper

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e .
```

---

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your favorite editor
```

**Required settings:**

```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# LLM (choose one)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# OR
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
```

---

## Step 4: Verify Installation

```bash
# Test Python imports
python -c "import semantic_mapper; print('✅ Package installed')"

# Test Neo4j connection
python -c "
from semantic_mapper.graph import Neo4jConnection
conn = Neo4jConnection()
if conn.verify_connectivity():
    print('✅ Neo4j connected')
else:
    print('❌ Neo4j connection failed')
"
```

---

## Step 5: Launch the Application

```bash
streamlit run src/semantic_mapper/ui/app.py
```

Your browser should open to `http://localhost:8501`

---

## Step 6: Try the E-commerce Example

### 6.1 Upload Data

1. Click **Upload Data**
2. Upload `data/examples/ecommerce_orders.csv`
3. Keep default settings
4. Click **Ingest Data**
5. ✅ You should see 10 records ingested

### 6.2 Define Domain

1. Click **Define Domain**
2. Enter this description:

   ```
   This is an e-commerce system. Customers place orders for products.
   Each order can contain multiple items with quantities and prices.
   Orders have shipping addresses and status tracking.
   ```

3. Click **Generate Proposal**
4. Wait 30-60 seconds ⏳
5. ✅ Review the proposed ontology

### 6.3 Review Ontology

1. Click **Review Ontology**
2. Examine the classes and relationships
3. Click **✅ Accept Ontology**
4. ✅ Ontology is now saved in Neo4j!

### 6.4 Create Sample Instances (Manual)

1. Click **Materialize Graph**
2. Select a class (e.g., "Customer")
3. Fill in properties:
   - name: "John Smith"
   - email: "john@example.com"
4. Click **Create Instance**
5. Repeat for other classes

### 6.5 Query Your Data

1. Click **Query Data**
2. Try natural language:
   ```
   Show me all instances
   ```
3. Click **Translate & Execute**
4. ✅ See the generated Cypher and results!

---

## Common Issues

### Neo4j Connection Failed

**Problem:** Can't connect to Neo4j

**Solution:**
- Check Neo4j is running
- Verify credentials in `.env`
- Try connecting with Neo4j Browser at `http://localhost:7474`

### LLM API Error

**Problem:** "API key not found" or "Invalid API key"

**Solution:**
- Check API key in `.env`
- Ensure no extra spaces
- Verify key is valid on provider's website

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
- Ensure virtual environment is activated
- Re-run `pip install -e .`
- Check Python version with `python --version`

---

## Next Steps

Once you've completed the example:

1. **Try your own data** — Upload your CSV/JSON files
2. **Experiment with feedback** — Request ontology modifications
3. **Explore Cypher** — Learn to write queries directly
4. **Read the docs** — See `docs/ontology_evolution_example.md`

---

## Getting Help

- Check README.md for detailed documentation
- Review examples in `data/examples/`
- Open an issue on GitHub
- Check Neo4j browser at `http://localhost:7474` to inspect the graph

---

## Cleaning Up

To reset and start fresh:

1. Go to **Settings** page in the app
2. Click **Clear Session Data** (clears UI state)
3. Click **Clear Neo4j Database** (removes all data)

Or manually in Neo4j Browser:

```cypher
// Delete everything
MATCH (n) DETACH DELETE n
```

---

## Success Checklist

- [ ] Neo4j running and connected
- [ ] LLM API key configured
- [ ] Streamlit app launched
- [ ] Example data uploaded
- [ ] Ontology proposal generated
- [ ] Ontology accepted and saved
- [ ] Sample instances created
- [ ] Query executed successfully

🎉 **Congratulations!** You're ready to build semantic graphs!

---

## What You've Learned

1. How to ingest heterogeneous data
2. How LLMs propose ontologies
3. How to provide feedback and iterate
4. How ontologies are stored in Neo4j
5. How natural language maps to Cypher

**Remember:** This is a *human-in-the-loop* system. The LLM assists, but you're in control.
