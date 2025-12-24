"""
SemantiCore - Main Application
Matches ui_example/App.tsx design and structure exactly.
"""

import streamlit as st
import sys
import uuid
from pathlib import Path

# Initialize session state
if "view" not in st.session_state:
    st.session_state.view = "overview"  # overview, creating, project_detail
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None
if "projects" not in st.session_state:
    st.session_state.projects = [
        {
            "id": "1",
            "name": "Clinical Pathway Engine",
            "domain": "Oncology Trials",
            "description": "Formalizing the relationship between patient biomarkers and trial eligibility.",
            "version": "2",
            "lastModified": "2h ago",
            "nodeCount": 18,
            "dataSources": [{"name": "trial_data.csv"}],
            "relationCount": "2.4k"
        }
    ]
# Wizard state
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = "setup"
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {
        "project_name": "",
        "description": "",
        "files": [],
        "primitives": [],
        "ontology": None,
        "is_processing": False
    }

st.set_page_config(
    page_title="SemantiCore",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS - matching ui_example exactly
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #080808;
        color: #f5f5f5;
    }

    /* Remove default padding */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Sidebar matching ui_example/Sidebar.tsx */
    [data-testid="stSidebar"] {
        background-color: #0d0d0d !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #0d0d0d;
    }

    /* Custom scrollbar */
    .custom-scrollbar::-webkit-scrollbar,
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    .custom-scrollbar::-webkit-scrollbar-track,
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb,
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover,
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    /* Glassmorphism */
    .glass {
        background: rgba(23, 23, 23, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Buttons */
    .stButton > button {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.6);
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(255, 255, 255, 0.2);
        color: white;
        background: rgba(255, 255, 255, 0.05);
    }

    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar matching ui_example/Sidebar.tsx"""
    with st.sidebar:
        # Brand - SemantiCore
        st.markdown("""
        <div style="padding: 2rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="position: relative;">
                    <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #2563eb 0%, #6366f1 100%); border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 25px rgba(37, 99, 235, 0.4);">
                        <svg width="20" height="20" fill="white" viewBox="0 0 24 24">
                            <rect x="3" y="3" width="18" height="18" rx="2"/>
                        </svg>
                    </div>
                    <div style="position: absolute; bottom: -4px; right: -4px; width: 16px; height: 16px; background: #10b981; border-radius: 50%; border: 2px solid #0d0d0d; display: flex; align-items: center; justify-content: center;">
                        <svg width="8" height="8" fill="white" viewBox="0 0 24 24">
                            <polygon points="13,2 3,14 12,14 11,22 21,10 12,10" fill="currentColor"/>
                        </svg>
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.875rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em;">SemantiCore</div>
                    <div style="display: flex; align-items: center; gap: 0.375rem; margin-top: 0.125rem;">
                        <div style="width: 4px; height: 4px; background: #60a5fa; border-radius: 50%;"></div>
                        <span style="font-size: 0.5rem; font-weight: 900; color: rgba(96, 165, 250, 0.8); text-transform: uppercase; letter-spacing: 0.2em;">System Core</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='padding: 1rem; padding-bottom: 2rem;'>", unsafe_allow_html=True)

        # Hub Overview button
        if st.button("🧭 Hub Overview", key="sidebar_home", use_container_width=True):
            st.session_state.view = "overview"
            st.session_state.current_project_id = None
            st.rerun()

        # New Deployment button
        if st.button("➕ New Deployment", key="sidebar_new", use_container_width=True):
            st.session_state.view = "creating"
            st.session_state.current_project_id = None
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Active Nodes section
        st.markdown("""
        <div style="padding: 0 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding: 0 0.5rem;">
                <span style="font-size: 0.625rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.2em;">Active Nodes</span>
                <span style="font-size: 0.563rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.1);">{} INSTANCE</span>
            </div>
        </div>
        """.format(len(st.session_state.projects)), unsafe_allow_html=True)

        # Project list
        for project in st.session_state.projects:
            is_active = st.session_state.current_project_id == project["id"]
            if st.button(
                f"{'📍 ' if is_active else '📦 '}{project['name'][:20]}",
                key=f"project_{project['id']}",
                use_container_width=True
            ):
                st.session_state.view = "project_detail"
                st.session_state.current_project_id = project["id"]
                st.rerun()

        # System Load widget
        st.markdown("""
        <div style="margin: 2rem 1rem 1rem 1rem; padding: 1.25rem; background: #111; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <svg width="14" height="14" fill="#10b981" viewBox="0 0 24 24">
                    <rect x="4" y="4" width="6" height="6" rx="1"/>
                    <rect x="4" y="14" width="6" height="6" rx="1"/>
                    <rect x="14" y="4" width="6" height="6" rx="1"/>
                    <rect x="14" y="14" width="6" height="6" rx="1"/>
                </svg>
                <span style="font-size: 0.625rem; font-weight: 900; color: rgba(255, 255, 255, 0.3); text-transform: uppercase; letter-spacing: 0.15em;">System Load</span>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.563rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.2); margin-bottom: 0.5rem; text-transform: uppercase;">
                    <span>Memory</span>
                    <span style="color: rgba(16, 185, 129, 0.6);">32%</span>
                </div>
                <div style="height: 4px; background: rgba(255, 255, 255, 0.05); border-radius: 999px; overflow: hidden;">
                    <div style="width: 32%; height: 100%; background: rgba(16, 185, 129, 0.4);"></div>
                </div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.563rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.2); margin-bottom: 0.5rem; text-transform: uppercase;">
                    <span>Reasoning</span>
                    <span style="color: rgba(37, 99, 235, 0.6);">Optimized</span>
                </div>
                <div style="height: 4px; background: rgba(255, 255, 255, 0.05); border-radius: 999px; overflow: hidden;">
                    <div style="width: 75%; height: 100%; background: rgba(37, 99, 235, 0.4);"></div>
                </div>
            </div>
            <div style="margin-top: 1.25rem; padding-top: 1.25rem; border-top: 1px solid rgba(255, 255, 255, 0.03); display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; gap: -0.375rem;">
                    <div style="width: 20px; height: 20px; background: rgba(255, 255, 255, 0.05); border: 2px solid #111; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <div style="width: 6px; height: 6px; background: rgba(255, 255, 255, 0.2); border-radius: 50%;"></div>
                    </div>
                </div>
                <span style="font-size: 0.5rem; font-weight: 900; color: rgba(255, 255, 255, 0.1); text-transform: uppercase; letter-spacing: -0.02em;">Cluster: 0x82A</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_header():
    """Render top header matching ui_example/App.tsx"""
    active_project = None
    if st.session_state.current_project_id:
        active_project = next((p for p in st.session_state.projects if p["id"] == st.session_state.current_project_id), None)

    is_creating = st.session_state.view == "creating"
    is_overview = st.session_state.view == "overview"

    status_html = ""
    if active_project:
        status_html = f"""
        <div class="flex items-center gap-3 animate-in fade-in">
            <span style="font-size: 0.563rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.2em;">Active:</span>
            <h1 style="font-size: 0.75rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; color: #60a5fa; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{active_project['name']}</h1>
            <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 0.125rem 0.5rem; border-radius: 999px;">
                <div style="width: 4px; height: 4px; background: #10b981; border-radius: 50%;"></div>
                <span style="font-size: 0.438rem; font-weight: 900; color: #10b981; text-transform: uppercase; letter-spacing: -0.02em;">Verified</span>
            </div>
        </div>
        """
    elif is_creating:
        status_html = """
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <svg width="12" height="12" fill="#f59e0b" viewBox="0 0 24 24">
                <polygon points="13,2 3,14 12,14 11,22 21,10 12,10" fill="currentColor"/>
            </svg>
            <h1 style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; color: rgba(255, 255, 255, 0.4);">Initializing Core</h1>
        </div>
        """
    else:
        status_html = """
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <svg width="12" height="12" fill="rgba(255,255,255,0.1)" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            <h1 style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; color: rgba(255, 255, 255, 0.1);">Global Orchestration</h1>
        </div>
        """

    st.markdown(f"""
    <div style="height: 56px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem; background: #0d0d0d; position: sticky; top: 0; z-index: 20;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; padding: 0.375rem 0.75rem; border-radius: 0.5rem; transition: all 0.2s; {'background: rgba(37, 99, 235, 0.1); color: #60a5fa;' if is_overview else 'color: rgba(255, 255, 255, 0.2);'}">
                🧭 Overview
            </div>
            <div style="width: 1px; height: 16px; background: rgba(255, 255, 255, 0.05); margin: 0 0.25rem;"></div>
            {status_html}
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.25rem 0.75rem; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 999px; font-size: 0.5rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.3); text-transform: uppercase; letter-spacing: 0.15em;">
                <div style="display: flex; align-items: center; gap: 0.375rem;">
                    <div style="width: 4px; height: 4px; background: #60a5fa; border-radius: 50%;"></div>
                    <span>Engine: v3.1</span>
                </div>
                <div style="width: 1px; height: 12px; background: rgba(255, 255, 255, 0.1);"></div>
                <div style="display: flex; align-items: center; gap: 0.375rem;">
                    <svg width="12" height="12" fill="#10b981" viewBox="0 0 24 24">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    <span>Secure</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_overview():
    """Render overview page matching ui_example/App.tsx overview section"""

    # TEST: Simple HTML to see if rendering works at all
    st.write("# Overview")
    st.write("Central orchestration hub for domain-specific knowledge architectures.")

    st.markdown("""
    <div style="padding: 2.5rem 3rem; max-width: 1800px; margin: 0 auto;" class="animate-in">
        <div style="margin-bottom: 3.5rem; display: flex; justify-content: space-between; align-items: end;">
            <div>
                <h2 style="font-size: 2.25rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; margin-bottom: 0.5rem;">Overview</h2>
                <p style="color: rgba(255, 255, 255, 0.3); font-weight: 500; font-size: 1.125rem; max-width: 48rem; line-height: 1.75;">Central orchestration hub for domain-specific knowledge architectures.</p>
            </div>
            <div style="padding: 1rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1rem; display: flex; align-items: center; gap: 1rem; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);">
                <div style="width: 40px; height: 40px; background: rgba(16, 185, 129, 0.1); border-radius: 0.75rem; display: flex; align-items: center; justify-center; border: 1px solid rgba(16, 185, 129, 0.2);">
                    <svg width="20" height="20" fill="#10b981" viewBox="0 0 24 24">
                        <rect x="4" y="4" width="6" height="6" rx="1"/>
                        <rect x="4" y="14" width="6" height="6" rx="1"/>
                        <rect x="14" y="4" width="6" height="6" rx="1"/>
                        <rect x="14" y="14" width="6" height="6" rx="1"/>
                    </svg>
                </div>
                <div>
                    <div style="font-size: 0.5rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.125rem;">Engine Load</div>
                    <div style="font-size: 1.25rem; font-weight: 900; font-style: italic; letter-spacing: -0.02em;">14%</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Project grid
    cols = st.columns(4)

    for idx, project in enumerate(st.session_state.projects[:3]):
        with cols[idx]:
            if st.button(
                f"📦 {project['name']}",
                key=f"overview_project_{project['id']}",
                use_container_width=True
            ):
                st.session_state.view = "project_detail"
                st.session_state.current_project_id = project["id"]
                st.rerun()

            st.markdown(f"""
            <div style="padding: 1.5rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1.5rem; min-height: 18rem; display: flex; flex-direction: column; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">
                    <div style="width: 48px; height: 48px; background: rgba(37, 99, 235, 0.1); border: 1px solid rgba(37, 99, 235, 0.2); border-radius: 1rem; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" fill="none" stroke="#60a5fa" stroke-width="2" viewBox="0 0 24 24">
                            <rect x="3" y="3" width="18" height="18" rx="2"/>
                        </svg>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.5rem; font-weight: 900; color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 0.25rem 0.5rem; border-radius: 0.375rem; text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid rgba(16, 185, 129, 0.2);">v{project['version']}.0.4</span>
                        <div style="font-size: 0.5rem; color: rgba(255, 255, 255, 0.2); font-family: 'JetBrains Mono', monospace; text-transform: uppercase; margin-top: 0.25rem; font-style: italic;">{project['lastModified']}</div>
                    </div>
                </div>
                <div style="flex: 1;">
                    <h3 style="font-size: 1.25rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; margin-bottom: 0.75rem;">{project['name']}</h3>
                    <p style="font-size: 0.75rem; color: rgba(255, 255, 255, 0.3); font-weight: 500; line-height: 1.5; margin-bottom: 1.5rem;">{project['description'][:80]}...</p>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="display: flex; gap: 1rem;">
                        <div>
                            <div style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; color: rgba(255, 255, 255, 0.2); margin-bottom: 0.25rem;">Nodes</div>
                            <div style="font-size: 1rem; font-weight: 900; font-style: italic;">{project['nodeCount']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; color: rgba(255, 255, 255, 0.2); margin-bottom: 0.25rem;">Sources</div>
                            <div style="font-size: 1rem; font-weight: 900; font-style: italic; color: rgba(96, 165, 250, 0.8);">{len(project['dataSources'])}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # New Deployment card
    with cols[min(len(st.session_state.projects), 3)]:
        if st.button("➕ Start New Deployment", key="new_deployment_card", use_container_width=True):
            st.session_state.view = "creating"
            st.rerun()

        st.markdown("""
        <div style="padding: 1.5rem; min-height: 18rem; border: 2px dashed rgba(255, 255, 255, 0.05); border-radius: 1.5rem; background: rgba(255, 255, 255, 0.01); cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; transition: all 0.3s;">
            <div style="width: 64px; height: 64px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1.5rem; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                <svg width="32" height="32" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="2" viewBox="0 0 24 24">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </div>
            <div style="font-size: 1.25rem; font-weight: 900; text-transform: uppercase; font-style: italic; color: rgba(255, 255, 255, 0.2); margin-bottom: 0.5rem;">New Deployment</div>
            <div style="font-size: 0.563rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; color: rgba(255, 255, 255, 0.1);">Ontology Core v3.0</div>
        </div>
        """, unsafe_allow_html=True)


def render_project_detail():
    """Render project detail page"""
    project = next((p for p in st.session_state.projects if p["id"] == st.session_state.current_project_id), None)
    if not project:
        st.session_state.view = "overview"
        st.rerun()
        return

    st.markdown(f"""
    <div style="padding: 2rem 3rem; max-width: 1600px; margin: 0 auto;" class="animate-in">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;">
            <div style="padding: 1rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 0.5rem; font-weight: 900; text-transform: uppercase; color: rgba(255, 255, 255, 0.2); letter-spacing: 0.15em; margin-bottom: 0.5rem;">Ingested Records</div>
                <div style="font-size: 1.5rem; font-weight: 900; font-style: italic; color: #60a5fa; letter-spacing: -0.02em;">{(len(project['dataSources']) * 1150):,}</div>
            </div>
            <div style="padding: 1rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 0.5rem; font-weight: 900; text-transform: uppercase; color: rgba(255, 255, 255, 0.2); letter-spacing: 0.15em; margin-bottom: 0.5rem;">Ontological Nodes</div>
                <div style="font-size: 1.5rem; font-weight: 900; font-style: italic; letter-spacing: -0.02em;">{project['nodeCount']}</div>
            </div>
            <div style="padding: 1rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 0.5rem; font-weight: 900; text-transform: uppercase; color: rgba(255, 255, 255, 0.2); letter-spacing: 0.15em; margin-bottom: 0.5rem;">Relations</div>
                <div style="font-size: 1.5rem; font-weight: 900; font-style: italic; letter-spacing: -0.02em;">{project['relationCount']}</div>
            </div>
            <div style="padding: 1rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 0.5rem; font-weight: 900; text-transform: uppercase; color: rgba(255, 255, 255, 0.2); letter-spacing: 0.15em; margin-bottom: 0.5rem;">Stability</div>
                <div style="font-size: 1.5rem; font-weight: 900; font-style: italic; color: #10b981; letter-spacing: -0.02em;">98.2%</div>
            </div>
        </div>

        <div style="padding: 2rem; background: rgba(23, 23, 23, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 1.5rem; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                <svg width="16" height="16" fill="#60a5fa" viewBox="0 0 24 24">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                <h2 style="font-size: 1.125rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em;">Materialization Log</h2>
            </div>
            <div style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.4);">Recent entity resolutions and relationship mappings...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stepper():
    """Render pipeline stepper matching ProjectWizard.tsx"""
    steps = [
        ("setup", "Identity", "🔐"),
        ("frame", "Frame", "🔍"),
        ("ingest", "Ingest", "📥"),
        ("extract", "Extract", "📊"),
        ("propose", "Propose", "✨"),
        ("negotiate", "Negotiate", "💬"),
        ("graph", "Knowledge", "🕸️"),
        ("query", "Query", "⚡"),
    ]

    current_step = st.session_state.wizard_step
    current_idx = next((i for i, (key, _, _) in enumerate(steps) if key == current_step), 0)

    # Back button
    col1, col2 = st.columns([1, 20])
    with col1:
        if st.button("← Home", key="wizard_home"):
            st.session_state.view = "overview"
            st.session_state.wizard_step = "setup"
            st.session_state.wizard_data = {
                "project_name": "",
                "description": "",
                "files": [],
                "primitives": [],
                "ontology": None,
                "is_processing": False
            }
            st.rerun()

    with col2:
        stepper_html = '<div class="stepper-container" style="margin: 0;">'

        for idx, (key, label, icon) in enumerate(steps):
            if key == current_step:
                status = "active"
            elif idx < current_idx:
                status = "completed"
            else:
                status = "pending"

            stepper_html += f'''
            <div class="step-badge {status}">
                <span class="step-icon">{icon}</span>
                <span class="step-label">{label}</span>
            </div>
            '''

            if idx < len(steps) - 1:
                stepper_html += '<div class="step-divider"></div>'

        stepper_html += '</div>'
        st.markdown(stepper_html, unsafe_allow_html=True)


def wizard_step_setup():
    """Step 1: Identity - Project Name"""
    st.markdown("""
    <div style="max-width: 42rem; width: 100%; margin: 0 auto; padding: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
            <div style="width: 48px; height: 48px; background: rgba(37, 99, 235, 0.1); border: 1px solid rgba(37, 99, 235, 0.2); border-radius: 1rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);">
                <span style="font-size: 1.5rem;">🔐</span>
            </div>
            <div>
                <h2 style="font-size: 1.875rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; margin: 0;">Deployment Identity</h2>
                <p style="font-size: 0.563rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.2em; margin: 0.25rem 0 0 0;">Canonical Target</p>
            </div>
        </div>
        <p style="color: rgba(255, 255, 255, 0.4); margin-bottom: 2rem; font-size: 0.875rem; line-height: 1.75; font-weight: 500;">Assign a unique identifier for this deployment. This name serves as the canonical root for all versioned ontology mutations.</p>
    </div>
    """, unsafe_allow_html=True)

    project_name = st.text_input(
        "Project Name",
        value=st.session_state.wizard_data.get("project_name", ""),
        placeholder="Ex: Precision_Oncology_X",
        key="project_name_input",
        label_visibility="collapsed"
    )

    st.session_state.wizard_data["project_name"] = project_name

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Configure Domain Framing →", disabled=not project_name, use_container_width=True):
        st.session_state.wizard_step = "frame"
        st.rerun()


def wizard_step_frame():
    """Step 2: Frame - Domain Description"""
    st.markdown(f"""
    <div style="max-width: 48rem; width: 100%; margin: 0 auto; padding: 2.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="width: 40px; height: 40px; background: rgba(37, 99, 235, 0.1); border: 1px solid rgba(37, 99, 235, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1.25rem;">🔍</span>
            </div>
            <div>
                <h2 style="font-size: 1.875rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; margin: 0;">Domain Framing</h2>
                <p style="font-size: 0.563rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.2em; margin: 0.25rem 0 0 0;">{st.session_state.wizard_data.get("project_name", "")}</p>
            </div>
        </div>
        <p style="color: rgba(255, 255, 255, 0.3); margin-bottom: 1.5rem; font-size: 0.875rem; line-height: 1.75; font-weight: 500;">Define the semantic rules for your domain knowledge graph.</p>
    </div>
    """, unsafe_allow_html=True)

    description = st.text_area(
        "Domain Description",
        value=st.session_state.wizard_data.get("description", ""),
        placeholder="Architect a knowledge graph for... Focus on relationships between...",
        height=320,
        key="description_input",
        label_visibility="collapsed"
    )

    st.session_state.wizard_data["description"] = description

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Initialize Ingestion →", disabled=not description, use_container_width=True):
        st.session_state.wizard_step = "ingest"
        st.rerun()


def wizard_step_ingest():
    """Step 3: Ingest - File Upload"""
    st.markdown("""
    <div style="max-width: 80rem; width: 100%; margin: 0 auto; padding: 2.5rem;">
        <h2 style="font-size: 1.875rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; text-align: center; margin-bottom: 2rem;">Source Ingestion</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        uploaded_files = st.file_uploader(
            "Drop Artifacts",
            accept_multiple_files=True,
            type=["csv", "txt", "json"],
            key="file_uploader"
        )

        if uploaded_files:
            files_data = []
            for file in uploaded_files:
                content = file.read().decode("utf-8")
                files_data.append({
                    "id": str(uuid.uuid4()),
                    "name": file.name,
                    "size": len(content),
                    "content": content[:10000]  # First 10k chars
                })
            st.session_state.wizard_data["files"] = files_data

    with col2:
        st.markdown(f"""
        <div class="glass" style="height: 450px; padding: 1.5rem; display: flex; flex-direction: column;">
            <div style="padding-bottom: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.563rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.15em; color: rgba(255, 255, 255, 0.2);">
                Buffer Status: {len(st.session_state.wizard_data.get("files", []))}
            </div>
            <div style="flex: 1; overflow-y: auto; padding-top: 1.5rem;">
        """, unsafe_allow_html=True)

        for file in st.session_state.wizard_data.get("files", []):
            st.markdown(f"""
            <div style="padding: 1rem; background: #0a0a0a; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 0.75rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="font-size: 1rem;">📄</span>
                        <div>
                            <div style="font-size: 0.625rem; font-weight: 900; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: -0.02em;">{file['name']}</div>
                            <div style="font-size: 0.5rem; color: rgba(255, 255, 255, 0.2); font-family: 'JetBrains Mono', monospace; text-transform: uppercase; margin-top: 0.125rem;">{(file['size'] / 1024):.1f} KB</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    if st.button("✨ Extract Primitives", disabled=len(st.session_state.wizard_data.get("files", [])) == 0, use_container_width=True):
        # Mock extraction - generate sample primitives
        primitives = [
            {"id": "1", "label": "Patient", "type": "entity", "evidence": "Found in data schema", "confidence": 0.95},
            {"id": "2", "label": "Treatment", "type": "entity", "evidence": "Medical records", "confidence": 0.92},
            {"id": "3", "label": "Biomarker", "type": "entity", "evidence": "Lab results", "confidence": 0.88},
            {"id": "4", "label": "has_biomarker", "type": "relation", "evidence": "Patient-biomarker link", "confidence": 0.90},
            {"id": "5", "label": "receives_treatment", "type": "relation", "evidence": "Treatment records", "confidence": 0.93},
        ]
        st.session_state.wizard_data["primitives"] = primitives
        st.session_state.wizard_step = "extract"
        st.rerun()


def wizard_step_extract():
    """Step 4: Extract - Primitives Table"""
    primitives = st.session_state.wizard_data.get("primitives", [])

    st.markdown("""
    <div style="max-width: 75rem; width: 100%; margin: 0 auto; padding: 2.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em;">Semantic Extraction</h2>
                <p style="font-size: 0.563rem; font-weight: 900; color: rgba(255, 255, 255, 0.3); text-transform: uppercase; letter-spacing: 0.2em; margin-top: 0.25rem;">Refined from Ingested Sources</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Table
    st.markdown("""
    <div style="max-width: 75rem; width: 100%; margin: 0 auto; padding: 0 2.5rem;">
        <div style="background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1.5rem; overflow: hidden; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);">
            <div style="display: grid; grid-template-columns: 60px 1fr 150px 100px 1fr; gap: 1rem; padding: 1rem 1.5rem; background: rgba(255, 255, 255, 0.01); border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.5rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.15em;">
                <div>Ref</div>
                <div>Primitive</div>
                <div>Type</div>
                <div style="text-align: center;">Score</div>
                <div>Source Evidence</div>
            </div>
    """, unsafe_allow_html=True)

    for idx, p in enumerate(primitives):
        type_color = {
            "entity": ("rgba(37, 99, 235, 0.1)", "#60a5fa", "rgba(37, 99, 235, 0.1)"),
            "relation": ("rgba(16, 185, 129, 0.1)", "#10b981", "rgba(16, 185, 129, 0.1)"),
            "attribute": ("rgba(251, 191, 36, 0.1)", "#fbbf24", "rgba(251, 191, 36, 0.1)")
        }.get(p["type"], ("rgba(255, 255, 255, 0.05)", "#fff", "rgba(255, 255, 255, 0.05)"))

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 60px 1fr 150px 100px 1fr; gap: 1rem; padding: 0.875rem 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.02); align-items: center;">
            <div style="font-size: 0.563rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.1); text-transform: uppercase;">{idx + 100}</div>
            <div style="font-size: 0.75rem; font-weight: 900; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: -0.02em;">{p['label']}</div>
            <div><span style="background: {type_color[0]}; color: {type_color[1]}; border: 1px solid {type_color[2]}; padding: 0.125rem 0.5rem; border-radius: 999px; font-size: 0.438rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.15em;">{p['type']}</span></div>
            <div style="font-size: 0.563rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.2); text-align: center;">{int(p['confidence'] * 100)}%</div>
            <div style="font-size: 0.563rem; font-family: 'JetBrains Mono', monospace; color: rgba(255, 255, 255, 0.1); font-style: italic;">"{p['evidence']}"</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Propose Formal Ontology →", use_container_width=True):
        # Mock ontology generation
        ontology = {
            "version": "1.0.0",
            "nodes": [
                {"id": "1", "label": "Patient", "type": "Class", "description": "Individual receiving medical care", "reasoning": "Core domain entity"},
                {"id": "2", "label": "Treatment", "type": "Class", "description": "Medical intervention or therapy", "reasoning": "Primary action concept"},
                {"id": "3", "label": "Biomarker", "type": "Class", "description": "Measurable biological indicator", "reasoning": "Observable property"},
            ]
        }
        st.session_state.wizard_data["ontology"] = ontology
        st.session_state.wizard_step = "propose"
        st.rerun()


def wizard_step_propose():
    """Step 5: Propose - Ontology Schema"""
    ontology = st.session_state.wizard_data.get("ontology", {})

    st.markdown(f"""
    <div style="max-width: 75rem; width: 100%; margin: 0 auto; padding: 2.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <div>
                <h2 style="font-size: 1.5rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em;">Proposed Schema v{ontology.get('version', '1.0.0')}</h2>
                <p style="font-size: 0.563rem; font-weight: 900; color: rgba(255, 255, 255, 0.3); text-transform: uppercase; letter-spacing: 0.2em; margin-top: 0.25rem;">AI Orchestrated Blueprint</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ontology nodes
    for node in ontology.get("nodes", []):
        st.markdown(f"""
        <div style="max-width: 75rem; width: 100%; margin: 0 auto 1rem auto; padding: 0 2.5rem;">
            <div style="padding: 1.5rem; background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 1rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); display: flex; justify-content: space-between; gap: 1.5rem;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                        <h3 style="font-size: 1.25rem; font-weight: 900; color: rgba(255, 255, 255, 0.9); text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; margin: 0;">{node['label']}</h3>
                        <span style="font-size: 0.438rem; font-weight: 900; color: #60a5fa; background: rgba(37, 99, 235, 0.1); padding: 0.125rem 0.5rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.15em; border: 1px solid rgba(37, 99, 235, 0.1);">{node['type']}</span>
                    </div>
                    <p style="font-size: 0.75rem; color: rgba(255, 255, 255, 0.4); line-height: 1.75; font-weight: 500; margin: 0;">{node['description']}</p>
                </div>
                <div style="flex: 0 0 33%; background: rgba(0, 0, 0, 0.4); padding: 1rem; border-radius: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <span style="font-size: 0.438rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.15em; display: block; margin-bottom: 0.25rem;">Logic Axiom</span>
                    <p style="font-size: 0.625rem; color: rgba(255, 255, 255, 0.3); font-family: 'JetBrains Mono', monospace; font-style: italic; line-height: 1.75; margin: 0;">{node.get('reasoning', 'Canonical Domain Class')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    if st.button("✅ Commit Blueprint", use_container_width=True):
        st.session_state.wizard_step = "negotiate"
        st.rerun()


def wizard_step_negotiate():
    """Step 6: Negotiate - Blueprint Locked"""
    st.markdown("""
    <div style="min-height: 70vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2.5rem;">
        <div style="width: 80px; height: 80px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 1.5rem; display: flex; align-items: center; justify-content: center; margin-bottom: 2rem; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);">
            <span style="font-size: 2.5rem;">✅</span>
        </div>
        <h2 style="font-size: 3rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em; margin-bottom: 1rem;">Blueprint Locked</h2>
        <p style="font-size: 1.125rem; color: rgba(255, 255, 255, 0.2); font-weight: 500; max-width: 32rem; line-height: 1.75; margin-bottom: 2.5rem;">Model integrity verified. Ready for deployment.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Deploy Knowledge Graph", use_container_width=True):
        st.session_state.wizard_step = "graph"
        st.rerun()


def wizard_step_graph():
    """Step 7: Graph - Knowledge Explorer"""
    st.markdown("""
    <div style="max-width: 87.5rem; width: 100%; margin: 0 auto; padding: 2.5rem; height: 80vh; display: flex; flex-direction: column;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.5rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em;">Knowledge Explorer</h2>
        </div>
        <div style="flex: 1; background: #050505; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 2.5rem; display: flex; align-items: center; justify-content: center; box-shadow: inset 0 4px 20px rgba(0, 0, 0, 0.5);">
            <div style="text-align: center; padding: 3rem;">
                <span style="font-size: 4rem; display: block; margin-bottom: 1rem;">🕸️</span>
                <p style="font-size: 1.25rem; font-weight: 900; color: rgba(255, 255, 255, 0.3); text-transform: uppercase; font-style: italic;">Graph Visualization Placeholder</p>
                <p style="font-size: 0.75rem; color: rgba(255, 255, 255, 0.2); margin-top: 0.5rem;">Interactive graph will render here</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Engine →", use_container_width=True):
        st.session_state.wizard_step = "query"
        st.rerun()


def wizard_step_query():
    """Step 8: Query - Cypher Engine"""
    st.markdown("""
    <div style="max-width: 75rem; width: 100%; margin: 0 auto; padding: 2.5rem;">
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 900; text-transform: uppercase; font-style: italic; letter-spacing: -0.02em;">Cypher Engine</h2>
            <p style="font-size: 0.5rem; font-weight: 900; color: rgba(255, 255, 255, 0.2); text-transform: uppercase; letter-spacing: 0.15em; font-family: 'JetBrains Mono', monospace; margin-top: 0.25rem;">Status: Materialized</p>
        </div>

        <div style="background: #050505; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 2rem; min-height: 400px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.875rem; color: rgba(96, 165, 250, 0.6); line-height: 1.75;">
                // Initialize query to begin...<br>
                // Example: MATCH (n:Patient)-[:HAS_BIOMARKER]->(b:Biomarker) RETURN n, b LIMIT 10
            </div>
        </div>

        <div style="background: #0d0d0d; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 1.5rem; padding: 0 2rem; height: 80px; display: flex; align-items: center; gap: 1rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
            <span style="font-size: 1.25rem;">⚡</span>
            <input style="flex: 1; background: transparent; border: none; outline: none; color: rgba(255, 255, 255, 0.8); font-size: 1.125rem; font-weight: 900; letter-spacing: -0.02em;" placeholder="Query semantic paths..." />
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Complete & Return Home", use_container_width=True):
        # Reset wizard and return to overview
        st.session_state.wizard_step = "setup"
        st.session_state.wizard_data = {
            "project_name": "",
            "description": "",
            "files": [],
            "primitives": [],
            "ontology": None,
            "is_processing": False
        }
        st.session_state.view = "overview"
        st.rerun()


def render_creating():
    """Render wizard directly in app"""
    # Add wizard-specific CSS
    st.markdown("""
    <style>
        /* Stepper styles */
        .stepper-container {
            display: flex;
            align-items: center;
            gap: 0.375rem;
            padding: 1rem 1.5rem;
            background: #0d0d0d;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            overflow-x: auto;
        }

        .step-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 0.75rem;
            border-radius: 0.75rem;
            transition: all 0.2s;
            flex-shrink: 0;
        }

        .step-badge.active {
            background: rgba(37, 99, 235, 0.1);
            color: #60a5fa;
            border: 1px solid rgba(37, 99, 235, 0.1);
        }

        .step-badge.completed {
            color: #10b981;
            border: 1px solid transparent;
        }

        .step-badge.pending {
            color: rgba(255, 255, 255, 0.1);
            border: 1px solid transparent;
        }

        .step-icon {
            font-size: 0.875rem;
        }

        .step-label {
            font-size: 0.563rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: -0.02em;
        }

        .step-badge.active .step-icon {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .step-divider {
            width: 8px;
            height: 1px;
            background: rgba(255, 255, 255, 0.05);
            flex-shrink: 0;
        }

        /* Input overrides for wizard */
        .stTextInput input, .stTextArea textarea {
            background: #0d0d0d !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 1rem !important;
            color: white !important;
            padding: 1.5rem !important;
            font-size: 1.25rem !important;
            font-weight: 900 !important;
        }

        .stTextArea textarea {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1rem !important;
            font-weight: 400 !important;
            line-height: 1.75 !important;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(37, 99, 235, 0.3) !important;
            box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.3) !important;
        }

        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: rgba(255, 255, 255, 0.05) !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            border: 2px dashed rgba(255, 255, 255, 0.05) !important;
            border-radius: 1.5rem !important;
            background: rgba(255, 255, 255, 0.01) !important;
            padding: 3rem !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: rgba(37, 99, 235, 0.3) !important;
            background: rgba(255, 255, 255, 0.02) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Render stepper
    render_stepper()

    # Render current step
    step = st.session_state.wizard_step

    if step == "setup":
        wizard_step_setup()
    elif step == "frame":
        wizard_step_frame()
    elif step == "ingest":
        wizard_step_ingest()
    elif step == "extract":
        wizard_step_extract()
    elif step == "propose":
        wizard_step_propose()
    elif step == "negotiate":
        wizard_step_negotiate()
    elif step == "graph":
        wizard_step_graph()
    elif step == "query":
        wizard_step_query()


def main():
    if st.session_state.view == "creating":
        # Wizard view - no sidebar or header
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
            }
            [data-testid="collapsedControl"] {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)
        render_creating()
    else:
        # Normal views - with sidebar and header
        render_sidebar()
        render_header()

        if st.session_state.view == "overview":
            render_overview()
        elif st.session_state.view == "project_detail":
            render_project_detail()


if __name__ == "__main__":
    main()
