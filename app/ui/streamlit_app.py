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

# Enhanced Header
st.markdown(
    """
    <div class="top-heading">
        <div style="width: 48px; height: 48px; border-radius: 999px; background: radial-gradient(circle at 30% 0, #22c55e, #16a34a 60%, #166534 100%); display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 0 32px rgba(34, 197, 94, 0.6);">🍳</div>
        <div>
            <h2>AI Recipe Recommender</h2>
            <p style="margin: 0.1rem 0 0 0; font-size: 0.85rem; color: #9ca3af;">Turn ingredients in your kitchen into delicious recipes in seconds</p>
        </div>
    </div>
    <hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #1f2937, transparent); margin: 0.5rem 0 1rem 0;">
    """,
    unsafe_allow_html=True,
)

# Auth check
if "user_info" not in st.session_state:
    # Show auth screen if not logged in
    auth_screen()
else:
    # Show app if logged in
    df = load_recipes()
    app_screen(df)
