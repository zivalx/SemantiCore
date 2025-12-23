"""
Query Page

Natural language and Cypher querying interface.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from semantic_mapper.graph import Neo4jConnection, QueryOperations
from semantic_mapper.llm import LLMFactory, QueryTranslator

st.set_page_config(
    page_title="Query | Semantic Mapper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Dark theme CSS matching ui_example
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0a0a0a;
        color: #f5f5f5;
    }

    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }

    .query-header {
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }

    .query-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: white;
        text-transform: uppercase;
        font-style: italic;
        letter-spacing: -0.02em;
        margin: 0 0 0.5rem 0;
    }

    .query-subtitle {
        font-size: 0.563rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: rgba(255, 255, 255, 0.2);
    }

    .info-box {
        background: rgba(37, 99, 235, 0.05);
        border-left: 4px solid #2563eb;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        color: #60a5fa;
        border: 1px solid rgba(37, 99, 235, 0.2);
        font-size: 0.875rem;
    }

    .cypher-display {
        background: #000;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 1.5rem;
        overflow: hidden;
        margin-top: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    .cypher-header {
        background: rgba(255, 255, 255, 0.02);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 0.75rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .cypher-label {
        font-size: 0.625rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: rgba(255, 255, 255, 0.4);
    }

    .cypher-code {
        padding: 2rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875rem;
        color: #60a5fa;
        line-height: 1.6;
        min-height: 200px;
        max-height: 400px;
        overflow-y: auto;
    }

    .result-container {
        background: rgba(23, 23, 23, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .result-header {
        font-size: 0.625rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: rgba(255, 255, 255, 0.3);
        margin-bottom: 1rem;
    }

    .query-input-wrapper {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(23, 23, 23, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0;
        transition: all 0.2s ease;
    }

    .query-input-wrapper:focus-within {
        border-color: #2563eb;
        box-shadow: 0 0 0 1px #2563eb;
    }

    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 1rem !important;
        padding: 1rem !important;
        font-size: 0.875rem !important;
        font-family: 'Inter', sans-serif !important;
        color: white !important;
    }

    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Query interface."""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="query-header">
            <div class="query-title">CYPHER ENGINE</div>
            <div class="query-subtitle">STATUS: MATERIALIZED</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("← Home", use_container_width=True):
            st.switch_page("app.py")

    # Get current project/ontology
    current_project = st.session_state.get("current_project")
    workflow_data = st.session_state.get("workflow_data")

    ontology_id = None
    if current_project and current_project.get("ontology"):
        ontology_id = current_project["ontology"]["ontology_id"]
    elif workflow_data and workflow_data.get("ontology"):
        ontology_id = workflow_data["ontology"]["ontology_id"]

    if not ontology_id:
        st.warning("No ontology found. Please create a project first.")
        if st.button("Create New Project"):
            st.switch_page("pages/new_project.py")
        st.stop()

    # Info box
    st.markdown("""
    <div class="info-box">
        <strong>Full Transparency:</strong> See every step from question → ontology mapping → Cypher query → results
    </div>
    """, unsafe_allow_html=True)

    # Query mode selection
    query_mode = st.radio(
        "Query Mode",
        ["Natural Language", "Direct Cypher"],
        horizontal=True,
    )

    if query_mode == "Natural Language":
        nl_query = st.text_area(
            "Your Question",
            height=120,
            placeholder="""Examples:
- How many instances do we have?
- Show me all relationships between entities
- What are the most common entity types?""",
        )

        if st.button("🔍 Translate & Execute", type="primary", use_container_width=True):
            if nl_query.strip():
                with st.spinner("Translating query..."):
                    try:
                        # Get schema context
                        conn = Neo4jConnection()
                        query_ops = QueryOperations(conn)
                        schema_context = query_ops.get_ontology_schema_context(ontology_id)

                        # Translate
                        llm = LLMFactory.create()
                        translator = QueryTranslator(llm)
                        result = translator.translate(
                            natural_language_query=nl_query,
                            ontology_schema=schema_context,
                        )

                        # Display translation with sophisticated Cypher box
                        st.markdown(f"""
                        <div class="cypher-display">
                            <div class="cypher-header">
                                <span class="cypher-label">GENERATED CYPHER</span>
                                <span style="font-size: 0.625rem; color: #60a5fa; font-weight: 700; cursor: pointer;">Copy Query</span>
                            </div>
                            <div class="cypher-code">{result.cypher_query}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Explanation in a glass container
                        st.markdown(f"""
                        <div class="result-container">
                            <div class="result-header">SEMANTIC MAPPING</div>
                            <p style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.6); line-height: 1.6;">{result.explanation}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Execute
                        with st.spinner("Executing query..."):
                            results = query_ops.execute_cypher(result.cypher_query)

                            st.markdown(f"""
                            <div class="result-container">
                                <div class="result-header">QUERY RESULTS ({len(results)} ROWS)</div>
                            </div>
                            """, unsafe_allow_html=True)

                            if results:
                                st.dataframe(results, use_container_width=True)
                            else:
                                st.markdown("""
                                <div style="padding: 2rem; text-align: center; color: rgba(255, 255, 255, 0.3); font-size: 0.875rem;">
                                    No results found
                                </div>
                                """, unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    else:  # Direct Cypher
        cypher_query = st.text_area(
            "Cypher Query",
            height=150,
            placeholder="MATCH (n:Instance) RETURN n LIMIT 10",
        )

        if st.button("▶️ Execute", type="primary", use_container_width=True):
            if cypher_query.strip():
                with st.spinner("Executing..."):
                    try:
                        conn = Neo4jConnection()
                        query_ops = QueryOperations(conn)
                        results = query_ops.execute_cypher(cypher_query)

                        st.markdown(f"""
                        <div class="result-container">
                            <div class="result-header">QUERY RESULTS ({len(results)} ROWS)</div>
                        </div>
                        """, unsafe_allow_html=True)

                        if results:
                            st.dataframe(results, use_container_width=True)
                        else:
                            st.markdown("""
                            <div style="padding: 2rem; text-align: center; color: rgba(255, 255, 255, 0.3); font-size: 0.875rem;">
                                No results found
                            </div>
                            """, unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Natural Language:**
        - "Show me all instances"
        - "How many instances of each class?"
        - "Find all relationships"

        **Cypher:**
        ```cypher
        // Get all instances
        MATCH (i:Instance) RETURN i LIMIT 10

        // Count by class
        MATCH (i:Instance)-[:INSTANCE_OF]->(c:OntologyClass)
        RETURN c.name, count(i) as count

        // Get relationships
        MATCH (s:Instance)-[r:RELATED]->(t:Instance)
        RETURN s, r, t LIMIT 10
        ```
        """)


if __name__ == "__main__":
    main()
