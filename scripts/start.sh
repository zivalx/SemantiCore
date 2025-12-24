#!/bin/bash
# SemantiCore - Local startup script (Unix/Mac/Linux)

set -e

echo "🔗 Starting SemantiCore..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your credentials."
    echo ""
    read -p "Press Enter to open .env for editing (Ctrl+C to cancel)..."
    ${EDITOR:-nano} .env
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e . > /dev/null 2>&1

# Check Neo4j connection
echo "🔍 Checking Neo4j connection..."
python -c "
from semantic_mapper.graph import Neo4jConnection
import sys
try:
    conn = Neo4jConnection()
    if conn.verify_connectivity():
        print('✅ Neo4j connected')
    else:
        print('❌ Neo4j not responding')
        print('   Make sure Neo4j is running on bolt://localhost:7687')
        print('   Or run: docker-compose up -d neo4j')
        sys.exit(1)
except Exception as e:
    print(f'❌ Neo4j connection failed: {e}')
    print('   Run: docker-compose up -d neo4j')
    sys.exit(1)
" || exit 1

echo ""
echo "🚀 Starting Streamlit application..."
echo "   URL: http://localhost:8501"
echo "   Neo4j Browser: http://localhost:7474"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run src/semantic_mapper/ui/app.py
