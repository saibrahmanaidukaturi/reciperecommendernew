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
    
    # Filters
    st.sidebar.header("Filters")
    cuisine = st.sidebar.selectbox(
        "Cuisine",
        ["Any"] + sorted(recommendation["Cuisine"].dropna().unique().tolist()),
    )
    course = st.sidebar.selectbox(
        "Course",
        ["Any"] + sorted(recommendation["Course"].dropna().unique().tolist()),
    )
    diet = st.sidebar.selectbox(
        "Diet",
        ["Any"] + sorted(recommendation["Diet"].dropna().unique().tolist()),
    )
    max_total_time = st.sidebar.slider(
        "Maximum time (minutes):", 
        0, 
        CONFIG.DEFAULT_MAX_TIME, 
        CONFIG.DEFAULT_MAX_TIME
    )
    
    placeholder = st.empty()
    
    if st.sidebar.button("Filter"):
        if (
            cuisine != "Any"
            or course != "Any"
            or diet != "Any"
            or max_total_time != CONFIG.DEFAULT_MAX_TIME
        ):
            results = filter_recipes(recommendation, cuisine, course, diet, max_total_time)
            applied_filters = []
            if cuisine != "Any":
                applied_filters.append(f"Cuisine: {cuisine}")
            if course != "Any":
                applied_filters.append(f"Course: {course}")
            if diet != "Any":
                applied_filters.append(f"Diet: {diet}")
            if max_total_time != CONFIG.DEFAULT_MAX_TIME:
                applied_filters.append(f"Max Time: {max_total_time} mins")
            
            if applied_filters:
                placeholder.write(f"Filters applied: {', '.join(applied_filters)}")
            else:
                placeholder.empty()
            _display_search_results(results)
        else:
            placeholder.empty()
            _display_search_results(recommendation)
    else:
        _display_search_results(recommendation)
    
    # Delete Account section
    st.markdown("---")
    with st.expander("Delete Account"):
        pwd = st.text_input(label="Confirm your password", type="password")
        st.button(
            label="Delete",
            on_click=firebase_auth.delete_account,
            args=[pwd],
            type="primary",
            key="delete_button",
        )


def _display_search_results(results):
    """Display recipe search results with pagination."""
    # Session defaults
    if "show_recipe_details" not in st.session_state:
        st.session_state.show_recipe_details = None
    if "page" not in st.session_state:
        st.session_state.page = 1
    
    # Details panel
    if st.session_state.show_recipe_details is not None and len(results) > 0:
        idx = st.session_state.show_recipe_details
        idx = max(0, min(idx, len(results) - 1))
        recipe = results.iloc[idx]
        _scroll_to_recipe_details()
        st.markdown('<a id="recipe-details"></a>', unsafe_allow_html=True)
        with st.expander("Recipe Details", expanded=True):
            _show_recipe_details(recipe)
        if st.button("Close Recipe", key="close_recipe_btn"):
            st.session_state.show_recipe_details = None
            st.rerun()
    
    if len(results) == 0:
        st.write("No recipes found. Try adjusting your filters.")
        return
    
    # Pagination
    per_page = 6
    total_pages = (len(results) - 1) // per_page + 1
    st.session_state.page = max(1, min(st.session_state.page, total_pages))
    
    start_idx = (st.session_state.page - 1) * per_page
    end_idx = start_idx + per_page
    page_results = results.iloc[start_idx:end_idx]
    
    cols = st.columns(3)
    for local_idx, (_, row) in enumerate(page_results.iterrows()):
        global_idx = start_idx + local_idx
        with cols[local_idx % 3]:
            img = _scrape_recipe_image(str(row.get("URL", "")))
            img_html = f'<img src="{img}" class="recipe-image">' if img else ""
            
            st.markdown(
                f"""
                <div class="recipe-card">
                    {img_html}
                    <div class="recipe-title">{row.get('RecipeName', '')}</div>
                    <div class="recipe-info">
                        Cuisine: {row.get('Cuisine', '')}<br>
                        Course: {row.get('Course', '')}<br>
                        Total Time: {int(row.get('TotalTimeInMins', 0))} minutes
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            btn_key = f"show_{global_idx}_{row.get('URL', '')}"
            if st.button("Show recipe", key=btn_key, use_container_width=True):
                st.session_state.show_recipe_details = global_idx
                st.rerun()
    
    st.markdown("---")
    
    # Pagination controls
    nav1, nav2, nav3 = st.columns([2, 8, 1])
    with nav1:
        if st.session_state.page > 1:
            if st.button("< Previous", key="prev_page"):
                st.session_state.page -= 1
                st.session_state.show_recipe_details = None
                st.rerun()
    with nav2:
        st.markdown(
            f'<div style="text-align: center;">Page {st.session_state.page} of {total_pages}</div>',
            unsafe_allow_html=True,
        )
    with nav3:
        if st.session_state.page < total_pages:
            if st.button("Next >", key="next_page"):
                st.session_state.page += 1
                st.session_state.show_recipe_details = None
                st.rerun()


def _show_recipe_details(recipe):
    """Show detailed view of a single recipe."""
    st.subheader(str(recipe.get("RecipeName", "")))
    
    img_url = _scrape_recipe_image(str(recipe.get("URL", "")))
    if img_url:
        st.image(img_url, width=300)
    
    st.write(f"**Ingredients:** {recipe.get('Ingredients', '')}")
    st.write(f"**Total Time:** {int(recipe.get('TotalTimeInMins', 0))} minutes")
    st.write(
        f"**Cuisine:** {recipe.get('Cuisine', '')}, "
        f"**Course:** {recipe.get('Course', '')}, "
        f"**Diet:** {recipe.get('Diet', '')}"
    )
    st.subheader("Instructions:")
    st.write(recipe.get("Instructions", ""))
    
    url = str(recipe.get("URL", "")).strip()
    if url:
        st.markdown(f"[View full recipe]({url})")


def _scrape_recipe_image(url: str):
    """Scrape recipe image from URL (cached)."""
    if not isinstance(url, str) or not url.strip():
        return None
    
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Site-specific selector
        div = soup.find("div", class_="recipe-image")
        img_tag = div.find("img") if div else None
        
        if img_tag and img_tag.get("src"):
            return urljoin(url, img_tag["src"])
        
        # Fallback: first reasonable <img>
        fallback = soup.find("img")
        if fallback and fallback.get("src"):
            return urljoin(url, fallback["src"])
        
    except Exception:
        return None
    
    return None
