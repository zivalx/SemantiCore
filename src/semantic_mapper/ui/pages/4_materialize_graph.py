"""Graph materialization page."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_mapper.graph import Neo4jConnection, InstanceOperations

st.set_page_config(page_title="Materialize Graph", page_icon="💾", layout="wide")

st.title("💾 Materialize Instance Graph")
st.markdown("""
Transform your canonical records into instance nodes according to the accepted ontology.

**Note:** This is a simplified materialization. In a production system, you would:
- Use LLM to map records to ontology classes
- Extract relationships from data
- Handle conflicts and uncertainties
""")

# Check prerequisites
if not st.session_state.get("accepted_ontology"):
    st.warning("⚠️ Please accept an ontology first!")
    if st.button("Go to Review Ontology"):
        st.switch_page("pages/3_review_ontology.py")
    st.stop()

if not st.session_state.get("canonical_records"):
    st.warning("⚠️ No data to materialize!")
    st.stop()

ontology_data = st.session_state.accepted_ontology
ontology = ontology_data["ontology"]
ontology_id = ontology_data["ontology_id"]

st.divider()

# Show ontology summary
with st.expander("🎯 Accepted Ontology", expanded=False):
    st.write(f"**Name:** {ontology.name}")
    st.write(f"**Classes:** {len(ontology.classes)}")
    st.write(f"**Relationships:** {len(ontology.relation_types)}")

# Materialization status
st.subheader("Materialization")

st.info("""
⚠️ **Development Note**

Full automatic materialization requires:
1. LLM-based record-to-class mapping
2. Entity resolution and deduplication
3. Relationship extraction from data
4. Conflict resolution

This is intentionally left as a manual/semi-automatic process to maintain transparency.
For this demo, we'll create sample instances.
""")

# Manual instance creation
st.divider()
st.subheader("Create Sample Instances")

if ontology.classes:
    selected_class = st.selectbox(
        "Select Class",
        options=[cls.name for cls in ontology.classes],
    )

    class_obj = next(cls for cls in ontology.classes if cls.name == selected_class)

    st.write(f"**Description:** {class_obj.description}")

    # Simple form for creating an instance
    st.write("**Create Instance:**")

    properties = {}
    for prop in class_obj.properties[:5]:  # Limit to 5 properties for simplicity
        prop_value = st.text_input(
            f"{prop.name} ({prop.data_type})",
            key=f"prop_{prop.name}",
            help=prop.description
        )
        if prop_value:
            properties[prop.name] = prop_value

    if st.button("Create Instance"):
        if properties:
            try:
                conn = Neo4jConnection()
                instance_ops = InstanceOperations(conn)

                instance_id = instance_ops.materialize_entity(
                    ontology_id=ontology_id,
                    class_name=selected_class,
                    properties=properties,
                )

                st.success(f"✅ Created instance: {instance_id}")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("Please provide at least one property")

# Show instance count
st.divider()
st.subheader("Instance Statistics")

try:
    conn = Neo4jConnection()
    instance_ops = InstanceOperations(conn)

    counts = instance_ops.count_instances_by_class(ontology_id)

    if counts:
        st.write("**Instances by Class:**")
        for class_name, count in counts.items():
            st.write(f"- **{class_name}**: {count} instances")

        total_instances = sum(counts.values())
        st.metric("Total Instances", total_instances)

        if total_instances > 0:
            if st.button("➡️ Next: Query Data", type="primary", use_container_width=True):
                st.switch_page("pages/5_query_data.py")
    else:
        st.info("No instances created yet")

except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")
