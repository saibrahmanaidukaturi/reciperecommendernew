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

# Header
st.markdown(
    """<div class="top-heading"><h2>🍳 AI Recipe Recommender</h2></div>""",
    unsafe_allow_html=True,
)
st.write("---")

# Auth check
if "user_info" not in st.session_state:
    # Show auth screen if not logged in
    auth_screen()
else:
    # Show app if logged in
    df = load_recipes()
    app_screen(df)
