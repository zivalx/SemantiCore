@echo off
REM SemantiCore - Local startup script (Windows)

echo.
echo Starting SemantiCore...
echo.

REM Check if .env exists
if not exist .env (
    echo No .env file found. Creating from template...
    copy .env.example .env
    echo.
    echo Created .env file. Please edit it with your credentials.
    echo Opening .env in notepad...
    notepad .env
    echo.
    pause
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -e . >nul 2>&1

REM Check Neo4j connection
echo Checking Neo4j connection...
python -c "from semantic_mapper.graph import Neo4jConnection; import sys; conn = Neo4jConnection(); sys.exit(0 if conn.verify_connectivity() else 1)"

if errorlevel 1 (
    echo.
    echo Neo4j connection failed!
    echo Make sure Neo4j is running on bolt://localhost:7687
    echo Or run: docker-compose up -d neo4j
    echo.
    pause
    exit /b 1
)

echo Neo4j connected
echo.
echo Starting Streamlit application...
echo    URL: http://localhost:8501
echo    Neo4j Browser: http://localhost:7474
echo.
echo Press Ctrl+C to stop
echo.

streamlit run src/semantic_mapper/ui/app.py
