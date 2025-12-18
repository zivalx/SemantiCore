# Deployment Guide

Complete guide for deploying Semantic Mapper locally, with Docker, or to the cloud.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
   - [Railway](#railway)
   - [Render](#render)
   - [Fly.io](#flyio)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.11+
- Neo4j (local or Docker)
- LLM API key (Anthropic or OpenAI)

### Quick Start

**Unix/Mac/Linux:**
```bash
# Make script executable
chmod +x scripts/start.sh

# Run
./scripts/start.sh
```

**Windows:**
```batch
# Just double-click scripts\start.bat or run:
scripts\start.bat
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Start Neo4j (if using Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5.15-community

# 5. Run application
streamlit run src/semantic_mapper/ui/app.py
```

**Access:**
- Application: http://localhost:8501
- Neo4j Browser: http://localhost:7474

---

## Docker Deployment

### Production Deployment

**1. Configure environment:**
```bash
# Create .env file
cat > .env <<EOF
NEO4J_PASSWORD=your_secure_password
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
EOF
```

**2. Start services:**
```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

**3. Access:**
- Application: http://localhost:8501
- Neo4j Browser: http://localhost:7474

**4. Stop services:**
```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

### Development with Docker

For development with live code reloading:

```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up

# Your code changes will be reflected immediately
```

### Docker Commands Reference

```bash
# Build only
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# View logs for specific service
docker-compose logs -f app
docker-compose logs -f neo4j

# Execute command in container
docker-compose exec app bash
docker-compose exec neo4j cypher-shell

# Restart a service
docker-compose restart app

# Scale (if needed)
docker-compose up -d --scale app=2
```

---

## Cloud Deployment

### Railway

**Best for:** Quick deployment, automatic HTTPS, built-in Neo4j plugin

**1. Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

**2. Initialize project:**
```bash
railway init
```

**3. Add Neo4j:**
- Go to Railway dashboard
- Add "Neo4j" plugin to your project
- Copy connection details

**4. Set environment variables:**
```bash
railway variables set NEO4J_URI=bolt://neo4j.railway.internal:7687
railway variables set NEO4J_USER=neo4j
railway variables set NEO4J_PASSWORD=<from-neo4j-plugin>
railway variables set LLM_PROVIDER=anthropic
railway variables set ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**5. Deploy:**
```bash
railway up
```

**Access:** Railway provides a URL like `https://semantic-mapper.up.railway.app`

**Cost:** ~$5-10/month for starter plan

---

### Render

**Best for:** Free tier available, straightforward deployment

**1. Create account at render.com**

**2. Connect GitHub repository**

**3. Create services:**

**Neo4j (Private Service):**
- Type: Private Service
- Environment: Docker
- Dockerfile: Create `Dockerfile.neo4j`:
  ```dockerfile
  FROM neo4j:5.15-community
  ENV NEO4J_AUTH=neo4j/your_password
  ```
- Disk: 10GB persistent disk at `/data`

**Application (Web Service):**
- Type: Web Service
- Environment: Docker
- Dockerfile: `Dockerfile`
- Environment variables:
  ```
  NEO4J_URI=bolt://semantic-mapper-neo4j:7687
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=<your-password>
  LLM_PROVIDER=anthropic
  ANTHROPIC_API_KEY=<your-key>
  ```

**4. Deploy:**
- Render auto-deploys on git push
- Or use `.deploy/render.yaml` for infrastructure as code

**Access:** `https://semantic-mapper.onrender.com`

**Cost:**
- Free tier: Limited hours/month
- Starter: $7/month per service

---

### Fly.io

**Best for:** Global deployment, edge computing, generous free tier

**1. Install Fly CLI:**
```bash
# Mac
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**2. Login:**
```bash
fly auth login
```

**3. Create app:**
```bash
fly launch
# Follow prompts, it will detect Dockerfile
```

**4. Set secrets:**
```bash
fly secrets set NEO4J_PASSWORD=your_password
fly secrets set ANTHROPIC_API_KEY=sk-ant-xxxxx
fly secrets set NEO4J_URI=bolt://your-neo4j-instance:7687
```

**5. Deploy:**
```bash
fly deploy
```

**6. Open app:**
```bash
fly open
```

**Neo4j Options for Fly.io:**
- Use Neo4j Aura (managed Neo4j)
- Use external Neo4j instance
- Deploy Neo4j on Fly (advanced)

**Cost:** Free tier includes 3 shared VMs

---

## Environment Configuration

### Required Variables

```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# LLM Provider (choose one)
LLM_PROVIDER=anthropic  # or "openai"

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OpenAI (GPT-4)
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4-turbo-preview
```

### Optional Variables

```bash
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Neo4j Performance Tuning
NEO4J_dbms_memory_pagecache_size=512M
NEO4J_dbms_memory_heap_max__size=1G
```

### Security Best Practices

1. **Never commit .env to git** (already in .gitignore)
2. **Use strong passwords** for Neo4j
3. **Rotate API keys** periodically
4. **Use secrets management** in production:
   - Railway: Built-in secrets
   - Render: Environment variables
   - Fly.io: `fly secrets`
   - Docker: Docker secrets or external vault

---

## Troubleshooting

### Neo4j Connection Failed

**Problem:** Can't connect to Neo4j

**Solutions:**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs semantic_mapper_neo4j

# Test connection
python -c "from semantic_mapper.graph import Neo4jConnection; conn = Neo4jConnection(); print('✅' if conn.verify_connectivity() else '❌')"

# Restart Neo4j
docker-compose restart neo4j
```

### Port Already in Use

**Problem:** Port 8501 or 7687 already in use

**Solutions:**
```bash
# Find process using port
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows

# Kill process or change port
export STREAMLIT_SERVER_PORT=8502
streamlit run src/semantic_mapper/ui/app.py --server.port=8502
```

### Docker Build Fails

**Problem:** Docker build errors

**Solutions:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs --tail=50 app
```

### LLM API Errors

**Problem:** API key invalid or quota exceeded

**Solutions:**
1. Verify API key in .env
2. Check API key on provider's website
3. Check rate limits and quotas
4. Try with different model:
   ```bash
   export ANTHROPIC_MODEL=claude-3-opus-20240229
   ```

### Memory Issues

**Problem:** Application crashes or Neo4j OOM

**Solutions:**
```bash
# Increase Neo4j memory in docker-compose.yml
NEO4J_dbms_memory_heap_max__size=2G

# Limit Docker container memory
docker-compose up -d --scale app=1 --memory=2g
```

### Streamlit Errors

**Problem:** Streamlit won't start

**Solutions:**
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/

# Reinstall dependencies
pip install --force-reinstall streamlit

# Check Python version
python --version  # Should be 3.11+
```

---

## Health Checks

### Application Health

```bash
# Health endpoint
curl http://localhost:8501/_stcore/health

# Should return: {"status": "ok"}
```

### Neo4j Health

```bash
# Cypher shell
docker-compose exec neo4j cypher-shell -u neo4j -p your_password

# Run test query
docker-compose exec neo4j cypher-shell -u neo4j -p your_password "RETURN 1"
```

### Full System Check

```bash
# Check all services
docker-compose ps

# All should show "Up" and "healthy"
```

---

## Backup and Restore

### Backup Neo4j Data

```bash
# Stop Neo4j
docker-compose stop neo4j

# Backup
docker run --rm \
  -v semantic_mapper_neo4j_data:/data \
  -v $(pwd)/backups:/backups \
  neo4j:5.15-community \
  neo4j-admin database dump neo4j --to=/backups/neo4j-backup.dump

# Start Neo4j
docker-compose start neo4j
```

### Restore Neo4j Data

```bash
# Stop Neo4j
docker-compose stop neo4j

# Restore
docker run --rm \
  -v semantic_mapper_neo4j_data:/data \
  -v $(pwd)/backups:/backups \
  neo4j:5.15-community \
  neo4j-admin database load neo4j --from=/backups/neo4j-backup.dump --overwrite-destination=true

# Start Neo4j
docker-compose start neo4j
```

---

## Monitoring

### Logs

```bash
# View all logs
docker-compose logs -f

# View app logs only
docker-compose logs -f app

# View last 100 lines
docker-compose logs --tail=100
```

### Metrics

```bash
# Docker stats
docker stats

# Neo4j metrics (in browser)
http://localhost:7474
# Navigate to "Database Information"
```

---

## Scaling

### Horizontal Scaling

```bash
# Run multiple app instances
docker-compose up -d --scale app=3

# Add load balancer (nginx)
# See nginx.conf example in /config
```

### Vertical Scaling

```bash
# Increase container resources
docker-compose up -d --memory=4g --cpus=2
```

---

## Next Steps

After successful deployment:

1. ✅ Upload example data
2. ✅ Create test ontology
3. ✅ Set up monitoring
4. ✅ Configure backups
5. ✅ Set up CI/CD
6. ✅ Add custom domain
7. ✅ Enable HTTPS
8. ✅ Set up user authentication

---

**Need help?** Check [README.md](../README.md) or open an issue.
