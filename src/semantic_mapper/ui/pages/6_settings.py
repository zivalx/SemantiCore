"""Settings and configuration page."""

import streamlit as st
import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_mapper.graph import Neo4jConnection

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings & Configuration")

# Database settings
st.subheader("Database Connection")

with st.expander("Neo4j Configuration", expanded=True):
    neo4j_uri = st.text_input(
        "Neo4j URI",
        value=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    )

    neo4j_user = st.text_input(
        "Neo4j User",
        value=os.getenv("NEO4J_USER", "neo4j"),
    )

    neo4j_password = st.text_input(
        "Neo4j Password",
        type="password",
        value=os.getenv("NEO4J_PASSWORD", ""),
    )

    if st.button("Test Connection"):
        try:
            conn = Neo4jConnection(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)
            if conn.verify_connectivity():
                st.success("✅ Connected to Neo4j!")
            else:
                st.error("❌ Failed to connect")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.divider()

# LLM settings
st.subheader("LLM Configuration")

with st.expander("LLM Provider", expanded=True):
    llm_provider = st.selectbox(
        "Provider",
        ["anthropic", "openai"],
        index=0 if os.getenv("LLM_PROVIDER", "anthropic") == "anthropic" else 1,
    )

    if llm_provider == "anthropic":
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
        )

        anthropic_model = st.selectbox(
            "Model",
            ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
            index=0,
        )

        st.info("Set these in your .env file for persistence")

    else:
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
        )

        openai_model = st.selectbox(
            "Model",
            ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            index=0,
        )

st.divider()

# Data management
st.subheader("Data Management")

with st.expander("Clear Data", expanded=False):
    st.warning("⚠️ Destructive Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Session Data", use_container_width=True):
            st.session_state.ingested_sources = []
            st.session_state.canonical_records = []
            st.session_state.current_proposal = None
            st.session_state.accepted_ontology = None
            st.success("✅ Session data cleared")
            st.rerun()

    with col2:
        if st.button("💣 Clear Neo4j Database", use_container_width=True, type="secondary"):
            if st.checkbox("I understand this will delete all data"):
                try:
                    conn = Neo4jConnection()
                    conn.clear_database()
                    st.success("✅ Database cleared")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

st.divider()

# System info
st.subheader("System Information")

with st.expander("Session State"):
    st.write("**Ingested Sources:**", len(st.session_state.get("ingested_sources", [])))
    st.write("**Canonical Records:**", len(st.session_state.get("canonical_records", [])))
    st.write("**Has Proposal:**", st.session_state.get("current_proposal") is not None)
    st.write("**Has Ontology:**", st.session_state.get("accepted_ontology") is not None)

with st.expander("Environment"):
    st.write("**NEO4J_URI:**", os.getenv("NEO4J_URI", "Not set"))
    st.write("**LLM_PROVIDER:**", os.getenv("LLM_PROVIDER", "Not set"))
    st.write("**ANTHROPIC_API_KEY:**", "Set" if os.getenv("ANTHROPIC_API_KEY") else "Not set")
    st.write("**OPENAI_API_KEY:**", "Set" if os.getenv("OPENAI_API_KEY") else "Not set")

# About
st.divider()
st.subheader("About")

st.markdown("""
**Semantic Mapper v0.1.0**

An ontology-first semantic graph platform that helps transform heterogeneous data
into queryable knowledge graphs using human-in-the-loop ontology design.

**Principles:**
- Ontology as a first-class artifact
- Explicit representation of uncertainty
- LLMs propose, humans decide
- Full traceability from data to ontology
- Transparency over automation

**GitHub:** [Link to repository]

**License:** MIT
""")
