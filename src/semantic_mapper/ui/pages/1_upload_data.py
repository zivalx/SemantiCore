"""Data upload page."""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_mapper.ingestion import IngesterFactory

st.set_page_config(page_title="Upload Data", page_icon="📁", layout="wide")

st.title("📁 Upload Data Sources")
st.markdown("""
Upload your data sources here. Supported formats: CSV, JSON, TXT, PDF, DOCX.

Data will be converted to a **canonical format** - no semantic interpretation happens yet.
""")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "json", "jsonl", "txt", "md", "pdf", "docx"],
    help="Upload your data source"
)

if uploaded_file is not None:
    st.divider()
    st.subheader("File Information")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size:,} bytes")

    with col2:
        file_ext = Path(uploaded_file.name).suffix.lower()
        st.write(f"**Type:** {file_ext}")
        st.write(f"**Supported:** {'✅' if IngesterFactory.is_supported(uploaded_file.name) else '❌'}")

    # Ingestion options
    st.divider()
    st.subheader("Ingestion Options")

    if file_ext == ".csv":
        delimiter = st.text_input("Delimiter", value=",")
        encoding = st.selectbox("Encoding", ["utf-8", "latin-1", "cp1252"], index=0)
        options = {"delimiter": delimiter, "encoding": encoding}

    elif file_ext in [".txt", ".md"]:
        split_by = st.selectbox(
            "Split by",
            ["paragraph", "line", "document"],
            index=0,
            help="How to split the text into records"
        )
        encoding = st.selectbox("Encoding", ["utf-8", "latin-1", "cp1252"], index=0)
        options = {"split_by": split_by, "encoding": encoding}

    elif file_ext == ".pdf":
        extract_by = st.selectbox(
            "Extract by",
            ["page", "document"],
            index=0,
            help="Extract page-by-page or entire document"
        )
        options = {"extract_by": extract_by}

    elif file_ext == ".docx":
        extract_by = st.selectbox(
            "Extract by",
            ["paragraph", "document"],
            index=0,
            help="Extract paragraph-by-paragraph or entire document"
        )
        options = {"extract_by": extract_by}

    else:
        options = {}

    # Ingest button
    if st.button("🚀 Ingest Data", type="primary", use_container_width=True):
        with st.spinner("Ingesting data..."):
            try:
                # Save uploaded file temporarily
                temp_path = Path(f"/tmp/{uploaded_file.name}")
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Ingest
                ingester = IngesterFactory.create_from_file(str(temp_path))
                result = ingester.ingest(str(temp_path), **options)

                # Store in session state
                if result.success:
                    st.session_state.ingested_sources.append({
                        "name": uploaded_file.name,
                        "source_id": str(result.provenance.source_id),
                        "record_count": result.record_count,
                    })
                    st.session_state.canonical_records.extend(result.records)

                    st.success(f"✅ Successfully ingested {result.record_count} records!")

                    # Show sample records
                    st.divider()
                    st.subheader("Sample Records")

                    sample_size = min(3, len(result.records))
                    for idx, record in enumerate(result.records[:sample_size]):
                        with st.expander(f"Record {idx + 1}"):
                            st.json(record.structured_fields)

                    if result.warnings:
                        st.warning("Warnings:\n" + "\n".join(result.warnings))

                else:
                    st.error("❌ Ingestion failed!")
                    for error in result.errors:
                        st.error(error)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Show ingested sources
if st.session_state.get("ingested_sources"):
    st.divider()
    st.subheader("Ingested Sources")

    for idx, source in enumerate(st.session_state.ingested_sources):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{source['name']}**")
            with col2:
                st.write(f"{source['record_count']} records")
            with col3:
                if st.button("🗑️", key=f"delete_{idx}"):
                    # TODO: Implement deletion
                    st.info("Deletion not yet implemented")

    st.divider()
    total_records = len(st.session_state.canonical_records)
    st.metric("Total Records", total_records)

    if total_records > 0:
        if st.button("➡️ Next: Define Domain", type="primary", use_container_width=True):
            st.switch_page("pages/2_define_domain.py")
