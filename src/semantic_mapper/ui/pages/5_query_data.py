"""Natural language query page."""

import streamlit as st
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_mapper.graph import Neo4jConnection, QueryOperations
from semantic_mapper.llm import LLMFactory, QueryTranslator

st.set_page_config(page_title="Query Data", page_icon="❓", layout="wide")

st.title("❓ Query Your Data")
st.markdown("""
Ask questions in natural language. The system will:
1. Show you how the question maps to ontology concepts
2. Generate a Cypher query
3. Execute the query and show results

**Transparency:** You see every step of the translation.
""")

# Check prerequisites
if not st.session_state.get("accepted_ontology"):
    st.warning("⚠️ Please accept an ontology first!")
    if st.button("Go to Review Ontology"):
        st.switch_page("pages/3_review_ontology.py")
    st.stop()

ontology_data = st.session_state.accepted_ontology
ontology_id = ontology_data["ontology_id"]

st.divider()

# Query input
st.subheader("Ask a Question")

query_mode = st.radio(
    "Query Mode",
    ["Natural Language", "Direct Cypher"],
    horizontal=True,
)

if query_mode == "Natural Language":
    nl_query = st.text_area(
        "Your Question",
        height=100,
        placeholder="Examples:\n- How many customers do we have?\n- Show me all orders from last month\n- Which products are most popular?",
    )

    if st.button("🔍 Translate & Execute", type="primary"):
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

                    # Store in session
                    st.session_state.last_translation = result

                    st.success("✅ Query translated!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Translation error: {str(e)}")
                    st.exception(e)
        else:
            st.warning("Please enter a question")

else:  # Direct Cypher
    cypher_query = st.text_area(
        "Cypher Query",
        height=150,
        placeholder="MATCH (n:Instance) RETURN n LIMIT 10",
    )

    if st.button("▶️ Execute Query", type="primary"):
        if cypher_query.strip():
            st.session_state.direct_cypher = cypher_query
            st.rerun()

# Show translation result
if st.session_state.get("last_translation"):
    st.divider()
    st.subheader("Translation Result")

    result = st.session_state.last_translation

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Your Question:**")
        st.info(result.natural_language)

        st.write("**Explanation:**")
        st.write(result.explanation)

        st.write("**Ontology Concepts Used:**")
        for concept in result.ontology_concepts_used:
            st.write(f"- {concept}")

    with col2:
        st.write("**Generated Cypher:**")
        st.code(result.cypher_query, language="cypher")

        st.metric("Confidence", f"{result.confidence:.0%}")

        if result.warnings:
            st.warning("**Warnings:**")
            for warning in result.warnings:
                st.write(f"- ⚠️ {warning}")

    # Execute
    if st.button("▶️ Execute This Query", type="primary"):
        st.session_state.execute_cypher = result.cypher_query
        st.rerun()

# Execute query
if st.session_state.get("execute_cypher") or st.session_state.get("direct_cypher"):
    st.divider()
    st.subheader("Query Results")

    query_to_run = st.session_state.get("execute_cypher") or st.session_state.get("direct_cypher")

    with st.spinner("Executing query..."):
        try:
            conn = Neo4jConnection()
            query_ops = QueryOperations(conn)

            results = query_ops.execute_cypher(query_to_run)

            if results:
                st.success(f"✅ Found {len(results)} results")

                # Show as table if possible
                if results:
                    st.dataframe(results, use_container_width=True)

                # Show as JSON
                with st.expander("📄 Raw JSON"):
                    st.json(results)

            else:
                st.info("No results found")

            # Clear execution flags
            st.session_state.execute_cypher = None
            st.session_state.direct_cypher = None

        except Exception as e:
            st.error(f"❌ Query execution error: {str(e)}")
            st.exception(e)

# Example queries
st.divider()
with st.expander("💡 Example Queries"):
    st.markdown("""
    **Natural Language Examples:**
    - "Show me all instances"
    - "How many instances of each class are there?"
    - "Find all relationships"

    **Cypher Examples:**
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
