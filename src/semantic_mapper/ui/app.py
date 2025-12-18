"""
Main Streamlit application.

Multi-page app for the semantic mapper platform.
"""

import streamlit as st
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Semantic Mapper",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "ingested_sources" not in st.session_state:
    st.session_state.ingested_sources = []
if "canonical_records" not in st.session_state:
    st.session_state.canonical_records = []
if "current_proposal" not in st.session_state:
    st.session_state.current_proposal = None
if "accepted_ontology" not in st.session_state:
    st.session_state.accepted_ontology = None
if "domain_description" not in st.session_state:
    st.session_state.domain_description = ""


def main():
    """Main application."""
    st.title("🔗 Semantic Mapper")
    st.markdown("""
    ### Ontology-First Semantic Graph Platform

    Transform heterogeneous data into queryable semantic graphs using a human-in-the-loop process.

    **Principles:**
    - 🎯 Ontology is a first-class artifact
    - 🤖 LLMs propose — humans decide
    - 📊 Every decision is traceable
    - 🔍 Transparency beats automation
    """)

    st.divider()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("""
    ### Workflow
    1. **Upload Data** - Ingest data sources
    2. **Define Domain** - Describe your domain
    3. **Review Ontology** - Review and refine proposals
    4. **Materialize Graph** - Create instance graph
    5. **Query Data** - Ask questions in natural language
    """)

    # Status overview
    st.sidebar.divider()
    st.sidebar.subheader("Status")

    sources_count = len(st.session_state.get("ingested_sources", []))
    records_count = len(st.session_state.get("canonical_records", []))
    has_proposal = st.session_state.get("current_proposal") is not None
    has_ontology = st.session_state.get("accepted_ontology") is not None

    st.sidebar.metric("Data Sources", sources_count)
    st.sidebar.metric("Records", records_count)
    st.sidebar.write(f"📋 Proposal: {'✅' if has_proposal else '⏳'}")
    st.sidebar.write(f"🎯 Ontology: {'✅' if has_ontology else '⏳'}")

    # Pages
    st.divider()
    st.subheader("Quick Links")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 Upload Data", use_container_width=True):
            st.switch_page("pages/1_upload_data.py")

    with col2:
        if st.button("🎯 Define Domain", use_container_width=True):
            st.switch_page("pages/2_define_domain.py")

    with col3:
        if st.button("🔍 Review Ontology", use_container_width=True):
            st.switch_page("pages/3_review_ontology.py")

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("💾 Materialize Graph", use_container_width=True):
            st.switch_page("pages/4_materialize_graph.py")

    with col5:
        if st.button("❓ Query Data", use_container_width=True):
            st.switch_page("pages/5_query_data.py")

    with col6:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/6_settings.py")

    # About
    st.divider()
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Semantic Mapper** is an ontology-first platform for transforming raw data
        into semantic graphs.

        Unlike traditional ETL systems that treat ontology as an afterthought, this system:
        - Makes ontology a first-class, versioned artifact stored in Neo4j
        - Represents uncertainty and alternatives explicitly
        - Ensures every semantic decision is traceable to source data
        - Prioritizes transparency over automation

        **Tech Stack:**
        - Python 3.11
        - Neo4j (graph database)
        - Streamlit (UI)
        - Claude/OpenAI (LLM proposals)
        - Pydantic (data validation)
        """)


if __name__ == "__main__":
    main()
