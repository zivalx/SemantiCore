"""Domain definition and ontology proposal page."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_mapper.llm import LLMFactory, OntologyProposer
from semantic_mapper.extraction import SemanticExtractor

st.set_page_config(page_title="Define Domain", page_icon="🎯", layout="wide")

st.title("🎯 Define Domain & Generate Ontology")
st.markdown("""
Describe your domain in natural language. The system will analyze your data and
propose an ontology that captures the semantic structure.

**Remember:** LLMs propose — you decide.
""")

# Check prerequisites
if not st.session_state.get("canonical_records"):
    st.warning("⚠️ Please upload data first!")
    if st.button("Go to Upload"):
        st.switch_page("pages/1_upload_data.py")
    st.stop()

# Show data summary
with st.expander("📊 Data Summary", expanded=False):
    st.write(f"**Sources:** {len(st.session_state.ingested_sources)}")
    st.write(f"**Total Records:** {len(st.session_state.canonical_records)}")

    # Show field analysis
    extractor = SemanticExtractor()
    analysis = extractor.analyze_field_patterns(st.session_state.canonical_records)

    st.write(f"**Unique Fields:** {analysis['unique_fields']}")

    with st.expander("Field Details"):
        for field_name, stats in sorted(analysis['field_stats'].items())[:20]:
            st.write(f"- **{field_name}**: appears {stats['count']} times")

st.divider()

# Domain description
st.subheader("1. Describe Your Domain")

domain_description = st.text_area(
    "Domain Description",
    value=st.session_state.get("domain_description", ""),
    height=200,
    placeholder="""Describe what your data represents. For example:

This data represents customer orders in an e-commerce system. Each order is placed by a customer
and contains multiple items. Customers have shipping addresses and payment information. Products
have categories, prices, and inventory levels. Orders can have different statuses like pending,
shipped, or delivered.""",
    help="Provide context about what entities exist, how they relate, and what the data means"
)

st.session_state.domain_description = domain_description

# Advanced options
with st.expander("⚙️ Advanced Options"):
    sample_size = st.slider(
        "Sample Size",
        min_value=5,
        max_value=50,
        value=10,
        help="Number of sample records to send to LLM"
    )

    iteration = st.number_input(
        "Iteration Number",
        min_value=1,
        max_value=10,
        value=1,
        help="Increment if refining a previous proposal"
    )

    previous_feedback = st.text_area(
        "Feedback from Previous Iteration (optional)",
        height=100,
        placeholder="E.g., 'Split Customer class into Person and Organization'",
    )

st.divider()

# Generate proposal
st.subheader("2. Generate Ontology Proposal")

if not domain_description.strip():
    st.info("💡 Please provide a domain description first")
else:
    if st.button("🤖 Generate Proposal", type="primary", use_container_width=True):
        with st.spinner("Generating ontology proposal... This may take 30-60 seconds."):
            try:
                # Get samples
                extractor = SemanticExtractor()
                samples = extractor.get_sample_records(
                    st.session_state.canonical_records,
                    sample_size=sample_size,
                    strategy="diverse"
                )

                # Get source IDs
                source_ids = [
                    src["source_id"]
                    for src in st.session_state.ingested_sources
                ]

                # Create proposer
                llm = LLMFactory.create()
                proposer = OntologyProposer(llm)

                # Generate proposal
                proposal = proposer.propose_ontology(
                    domain_description=domain_description,
                    data_samples=samples,
                    source_ids=source_ids,
                    iteration=iteration,
                    previous_feedback=previous_feedback if previous_feedback else None,
                )

                # Store in session state
                st.session_state.current_proposal = proposal

                st.success("✅ Ontology proposal generated!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating proposal: {str(e)}")
                st.exception(e)

# Show current proposal
if st.session_state.get("current_proposal"):
    st.divider()
    st.subheader("📋 Current Proposal")

    proposal = st.session_state.current_proposal

    # Overall explanation
    with st.expander("📖 Overall Explanation", expanded=True):
        st.write(proposal.overall_explanation)

        if proposal.assumptions:
            st.write("**Assumptions:**")
            for assumption in proposal.assumptions:
                st.write(f"- {assumption}")

        if proposal.open_questions:
            st.write("**Open Questions:**")
            for question in proposal.open_questions:
                st.write(f"- ❓ {question}")

    # Classes
    st.write(f"**Classes:** {len(proposal.class_proposals)}")
    for cls_prop in proposal.class_proposals:
        with st.expander(f"🏷️ {cls_prop.proposed_class.name}"):
            st.write(f"**Label:** {cls_prop.proposed_class.label}")
            st.write(f"**Description:** {cls_prop.proposed_class.description}")
            st.write(f"**Rationale:** {cls_prop.proposed_class.rationale}")
            st.write(f"**Confidence:** {cls_prop.confidence.score:.2f}")
            st.write(f"**Reasoning:** {cls_prop.confidence.reasoning}")

            if cls_prop.open_questions:
                st.write("**Questions:**")
                for q in cls_prop.open_questions:
                    st.write(f"- ❓ {q}")

    # Relationships
    st.write(f"**Relationships:** {len(proposal.relation_proposals)}")
    for rel_prop in proposal.relation_proposals:
        with st.expander(
            f"🔗 {rel_prop.proposed_relation.source_class} → "
            f"{rel_prop.proposed_relation.name} → "
            f"{rel_prop.proposed_relation.target_class}"
        ):
            st.write(f"**Label:** {rel_prop.proposed_relation.label}")
            st.write(f"**Description:** {rel_prop.proposed_relation.description}")
            st.write(f"**Cardinality:** {rel_prop.proposed_relation.cardinality}")
            st.write(f"**Confidence:** {rel_prop.confidence.score:.2f}")

    # Next step
    st.divider()
    if st.button("➡️ Review & Provide Feedback", type="primary", use_container_width=True):
        st.switch_page("pages/3_review_ontology.py")
