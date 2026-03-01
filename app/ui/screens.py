# app/ui/screens.py
import streamlit as st
import streamlit.components.v1 as components
from app.core.config import CONFIG
from app.ml.recommender import recommend, filter_recipes
from app.auth import firebase_auth


def _scroll_to_recipe_details():
    """Scroll to recipe details section."""
    components.html(
        """
        <script>
        const el = document.getElementById("recipe-details");
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        </script>
        """,
        height=0,
    )


def auth_screen():
    """Render authentication screen (login/signup/password reset)."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div class="auth-container">
                <h3 style="margin-bottom: 0.3rem; font-size: 1.4rem;">Welcome back</h3>
                <p style="margin-top: 0; margin-bottom: 1.2rem; color: #9ca3af; font-size: 0.9rem;">
                    Sign in to save your preferences and access personalized recipe recommendations
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    do_you_have_an_account = col2.selectbox(
        label="Do you have an account?",
        options=("Yes", "No", "I forgot my password"),
    )
    
    auth_form = col2.form(key="Authentication form", clear_on_submit=False)
    email = auth_form.text_input(label="Email")
    password = (
        auth_form.text_input(label="Password", type="password")
        if do_you_have_an_account in {"Yes", "No"}
        else None
    )
    
    auth_notification = col2.empty()
    
    if do_you_have_an_account == "Yes" and auth_form.form_submit_button(label="Sign In", use_container_width=True):
        with auth_notification, st.spinner("Signing in..."):
            firebase_auth.sign_in(email, password)
    
    elif do_you_have_an_account == "No" and auth_form.form_submit_button(label="Create Account", use_container_width=True):
        with auth_notification, st.spinner("Creating account..."):
            firebase_auth.create_account(email, password)
    
    elif do_you_have_an_account == "I forgot my password" and auth_form.form_submit_button(
        label="Send Password Reset Email", use_container_width=True
    ):
        with auth_notification, st.spinner("Sending password reset link..."):
            firebase_auth.reset_password(email)
    
    # Show messages
    if "auth_success" in st.session_state:
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success
    elif "auth_warning" in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning


def app_screen(df):
    """Render main app screen (for authenticated users)."""
    # Header with user info and sign out
    col1, col2, col3 = st.columns([2, 10, 2])
    
    with col2:
        email = st.session_state.user_info.get("email")
        st.markdown(
            f"""<div class="welcome-text"><h5>Welcome, <span style="color: var(--text-main); font-weight: 600;">{email}</span></h5></div>""",
            unsafe_allow_html=True,
        )
    
    with col3:
        with st.expander("Profile"):
            st.button(label="Sign Out", on_click=firebase_auth.sign_out, use_container_width=True)
    
    st.markdown("---")
    
    # Search / query with better styling
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.7), rgba(15, 23, 42, 0.9)); border-radius: 20px; padding: 1.5rem 1.8rem; border: 1px solid rgba(148, 163, 184, 0.15); margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.8rem 0; font-size: 1.1rem;">What would you like to cook today?</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    query = st.text_input(
        "Ingredients or recipe",
        label_visibility="collapsed",
        placeholder="e.g., chicken, spinach, garlic — or 'butter chicken'",
    )
    
    # Compute recommendations only when user clicks
    if st.button("Get Recommendations", use_container_width=True):
        q = query.strip()
        if not q:
            st.warning("Please enter ingredients or a recipe name.")
        else:
            with st.spinner("Finding recipes..."):
                st.session_state["recommendation_query"] = q
                st.session_state["recommendation"] = recommend(q, df)
                # reset paging/detail UI state
                st.session_state["page"] = 1
                st.session_state["show_recipe_details"] = None
                st.rerun()
    
    recommendation = st.session_state.get("recommendation")
    if recommendation is None:
        return
    
   
