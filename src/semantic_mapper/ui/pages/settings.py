"""
Settings Page

Configuration and preferences.
"""

import streamlit as st

st.set_page_config(
    page_title="Settings | Semantic Mapper",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

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
        max-width: 1000px;
    }

    .settings-header {
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }

    .settings-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: white;
        text-transform: uppercase;
        font-style: italic;
        letter-spacing: -0.02em;
        margin: 0 0 0.5rem 0;
    }

    .settings-section {
        background: rgba(23, 23, 23, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }

    .settings-section:hover {
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }

    .section-title {
        font-size: 0.625rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: rgba(255, 255, 255, 0.3);
        margin-bottom: 1.5rem;
    }

    .stTextInput input, .stSelectbox select {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem !important;
        color: white !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }

    .stSlider {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Settings page."""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="settings-header">
            <div class="settings-title">SYSTEM SETTINGS</div>
            <div style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; color: rgba(255, 255, 255, 0.2);">CONFIGURATION</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("← Home", use_container_width=True):
            st.switch_page("app.py")

    # LLM Settings
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">LLM Configuration</div>', unsafe_allow_html=True)

    llm_provider = st.selectbox(
        "Provider",
        ["Anthropic Claude", "OpenAI GPT"],
        help="Select your LLM provider"
    )

    api_key = st.text_input(
        "API Key",
        type="password",
        help="Your API key (stored in session only)"
    )

    if llm_provider == "Anthropic Claude":
        model = st.selectbox("Model", ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"])
    else:
        model = st.selectbox("Model", ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])

    st.markdown('</div>', unsafe_allow_html=True)

    # Neo4j Settings
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Neo4j Database</div>', unsafe_allow_html=True)

    neo4j_uri = st.text_input("URI", value="bolt://localhost:7687")
    neo4j_user = st.text_input("Username", value="neo4j")
    neo4j_password = st.text_input("Password", type="password")

    if st.button("Test Connection"):
        st.info("Connection test not implemented")

    st.markdown('</div>', unsafe_allow_html=True)

    # Application Settings
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Application</div>', unsafe_allow_html=True)

    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    default_sample_size = st.slider("Default Sample Size", 5, 50, 10)

    st.markdown('</div>', unsafe_allow_html=True)

    # Save button
    if st.button("Save Settings", type="primary", use_container_width=True):
        st.success("Settings saved successfully!")

    # Danger zone
    st.markdown("---")
    st.markdown('<div class="settings-section" style="border-color: #ef4444;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="color: #dc2626;">Danger Zone</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear All Projects", use_container_width=True):
            if st.checkbox("I understand this will delete all projects"):
                st.session_state.projects = []
                st.success("All projects cleared")

    with col2:
        if st.button("Reset Application", use_container_width=True):
            if st.checkbox("I understand this will reset everything"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("Application reset")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
