"""Ontology review and feedback page."""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_mapper.models.ontology import Ontology
from semantic_mapper.models.feedback import FeedbackAction
from semantic_mapper.graph import Neo4jConnection, OntologyOperations

st.set_page_config(page_title="Review Ontology", page_icon="🔍", layout="wide")

st.title("🔍 Review & Refine Ontology")
st.markdown("""
Review the proposed ontology and provide feedback. You can:
- ✅ Accept the proposal
- ✏️ Request modifications
- 🔄 Request a new proposal with guidance
""")

# Check prerequisites
if not st.session_state.get("current_proposal"):
    st.warning("⚠️ No proposal available. Please generate one first!")
    if st.button("Go to Define Domain"):
        st.switch_page("pages/2_define_domain.py")
    st.stop()

proposal = st.session_state.current_proposal

st.divider()

# Decision
st.subheader("Your Decision")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ Accept Ontology", type="primary", use_container_width=True):
        st.session_state.decision = "accept"

with col2:
    if st.button("✏️ Request Modifications", use_container_width=True):
        st.session_state.decision = "modify"

with col3:
    if st.button("🔄 Request New Proposal", use_container_width=True):
        st.session_state.decision = "revise"

# Handle decision
if st.session_state.get("decision") == "accept":
    st.divider()
    st.success("🎉 Accepting ontology proposal!")

    with st.spinner("Creating ontology in Neo4j..."):
        try:
            # Convert proposal to ontology
            ontology = Ontology(
                name=proposal.ontology_name,
                version="1.0.0",
                description=proposal.domain_description,
                domain=proposal.domain_description,
                classes=[cp.proposed_class for cp in proposal.class_proposals],
                relation_types=[rp.proposed_relation for rp in proposal.relation_proposals],
            )

            # Save to Neo4j
            conn = Neo4jConnection()
            ops = OntologyOperations(conn)

            # Initialize schema
            ops.initialize_schema()

            # Create ontology
            ontology_id = ops.create_ontology(ontology)

            # Mark as accepted
            ops.accept_ontology(ontology_id, ontology.version)

            # Store in session state
            st.session_state.accepted_ontology = {
                "ontology_id": str(ontology_id),
                "ontology": ontology,
                "accepted_at": datetime.utcnow().isoformat(),
            }

            st.success("✅ Ontology saved to Neo4j!")

            # Clear decision
            st.session_state.decision = None

            st.balloons()

            if st.button("➡️ Next: Materialize Graph", type="primary"):
                st.switch_page("pages/4_materialize_graph.py")

        except Exception as e:
            st.error(f"❌ Error saving ontology: {str(e)}")
            st.exception(e)

elif st.session_state.get("decision") == "modify":
    st.divider()
    st.subheader("Modification Requests")
    st.info("💡 Describe the changes you want. This will be used in the next iteration.")

    modifications = st.text_area(
        "What should be changed?",
        height=200,
        placeholder="""Examples:
- Rename 'User' class to 'Customer'
- Split 'Address' into 'ShippingAddress' and 'BillingAddress'
- Add a 'createdAt' property to 'Order' class
- Change relationship cardinality from many-to-many to one-to-many
""",
    )

    if st.button("Submit Feedback"):
        if modifications.strip():
            st.session_state.previous_feedback = modifications
            st.success("✅ Feedback recorded! Go back to 'Define Domain' to generate a new proposal.")
            st.session_state.decision = None

            if st.button("Go to Define Domain"):
                st.switch_page("pages/2_define_domain.py")
        else:
            st.warning("Please provide feedback")

elif st.session_state.get("decision") == "revise":
    st.divider()
    st.info("Going back to domain definition for a new proposal...")
    st.session_state.decision = None

    if st.button("Go to Define Domain"):
        st.switch_page("pages/2_define_domain.py")

# Show proposal details
st.divider()
st.subheader("Proposal Details")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 Summary", "🏷️ Classes", "🔗 Relationships"])

with tab1:
    st.write("**Ontology Name:**", proposal.ontology_name)
    st.write("**Domain:**", proposal.domain_description)
    st.write("**Overall Confidence:**", f"{proposal.confidence.score:.2f}")

    st.write("**Overall Explanation:**")
    st.write(proposal.overall_explanation)

    if proposal.assumptions:
        st.write("**Assumptions:**")
        for assumption in proposal.assumptions:
            st.write(f"- {assumption}")

    if proposal.open_questions:
        st.write("**Open Questions:**")
        for question in proposal.open_questions:
            st.write(f"- ❓ {question}")

with tab2:
    st.write(f"**Total Classes:** {len(proposal.class_proposals)}")

    for idx, cls_prop in enumerate(proposal.class_proposals):
        cls = cls_prop.proposed_class
        with st.expander(f"{idx + 1}. {cls.name}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Label:** {cls.label}")
                st.write(f"**Description:** {cls.description}")
                st.write(f"**Rationale:** {cls.rationale}")

                if cls.examples:
                    st.write("**Examples:**")
                    for ex in cls.examples:
                        st.write(f"- {ex}")

            with col2:
                st.metric("Confidence", f"{cls_prop.confidence.score:.0%}")

                if cls_prop.open_questions:
                    st.write("**Questions:**")
                    for q in cls_prop.open_questions:
                        st.write(f"❓ {q}")

with tab3:
    st.write(f"**Total Relationships:** {len(proposal.relation_proposals)}")

    for idx, rel_prop in enumerate(proposal.relation_proposals):
        rel = rel_prop.proposed_relation
        with st.expander(
            f"{idx + 1}. {rel.source_class} → {rel.name} → {rel.target_class}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Label:** {rel.label}")
                st.write(f"**Description:** {rel.description}")
                st.write(f"**Cardinality:** {rel.cardinality}")
                st.write(f"**Rationale:** {rel.rationale}")

            with col2:
                st.metric("Confidence", f"{rel_prop.confidence.score:.0%}")
