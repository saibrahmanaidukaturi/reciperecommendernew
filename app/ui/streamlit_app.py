# app/ui/streamlit_app.py
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from app.data.repository import load_recipes
from app.ui.screens import auth_screen, app_screen

# Page config
st.set_page_config(
    page_title="AI Recipe Recommender",
    page_icon="🍳",
    layout="wide",
)

# Load CSS
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
css_path = os.path.join(project_root, "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Clean Professional Header
st.markdown(
    """
    <div class="top-heading">
        <div style="
            width: 44px; height: 44px;
            border-radius: 10px;
            background: linear-gradient(135deg, #e67e22, #d35400);
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
            box-shadow: 0 2px 8px rgba(230,126,34,0.35);
            flex-shrink: 0;
        ">🍳</div>
        <div>
            <h2 style="color:#1a1a2e; font-weight:700; font-size:1.5rem; margin:0; letter-spacing:-0.3px;">AI Recipe Recommender</h2>
            <p style="margin:0.1rem 0 0 0; font-size:0.82rem; color:#6c757d;">Turn ingredients in your kitchen into delicious recipes in seconds</p>
        </div>
    </div>
    <hr style="border:none; border-top:1px solid #dee2e6; margin:0.75rem 0 1rem 0;" />
    """,
    unsafe_allow_html=True,
)

# Auth check
if "user_info" not in st.session_state:
    auth_screen()
else:
    df = load_recipes()
    app_screen(df)
