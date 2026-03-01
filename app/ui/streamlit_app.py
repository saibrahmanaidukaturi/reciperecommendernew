import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
import streamlit as st
from app.data.repository import load_recipes
from app.ui.screens import app_screen





st.set_page_config(layout="wide")

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
css_path = os.path.join(project_root, "styles.css")

if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """<div class="top-heading"><h2>🍳 AI Recipe Recommender</h2></div>""",
    unsafe_allow_html=True,
)
st.write("---")

df = load_recipes()
app_screen(df)