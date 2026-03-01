import streamlit as st
import streamlit.components.v1 as components

from app.core import session_keys as SK
from app.core.config import CONFIG
from app.ml.recommender import recommend, filter_recipes


def _scroll():
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


def _show_recipe(recipe):
    st.subheader(recipe.get("RecipeName", ""))

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


def _display_results(results):
    if SK.SHOW_RECIPE_DETAILS not in st.session_state:
        st.session_state[SK.SHOW_RECIPE_DETAILS] = None

    if SK.PAGE not in st.session_state:
        st.session_state[SK.PAGE] = 1

    if st.session_state[SK.SHOW_RECIPE_DETAILS] is not None and len(results) > 0:
        idx = st.session_state[SK.SHOW_RECIPE_DETAILS]
        idx = max(0, min(idx, len(results) - 1))
        recipe = results.iloc[idx]

        _scroll()
        st.markdown('<a id="recipe-details"></a>', unsafe_allow_html=True)

        with st.expander("Recipe Details", expanded=True):
            _show_recipe(recipe)
            if st.button("Close Recipe", key="close_btn"):
                st.session_state[SK.SHOW_RECIPE_DETAILS] = None
                st.rerun()

    if len(results) == 0:
        st.write("No recipes found.")
        return

    per_page = 6
    total_pages = (len(results) - 1) // per_page + 1

    start = (st.session_state[SK.PAGE] - 1) * per_page
    end = start + per_page
    page_results = results.iloc[start:end]

    cols = st.columns(3)

    for i, (_, row) in enumerate(page_results.iterrows()):
        global_idx = start + i
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="recipe-card">
                    <div class="recipe-title">{row.get('RecipeName','')}</div>
                    <div class="recipe-info">
                        Cuisine: {row.get('Cuisine','')}<br>
                        Course: {row.get('Course','')}<br>
                        Total Time: {int(row.get('TotalTimeInMins',0))} minutes
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Show recipe", key=f"show_{global_idx}"):
                st.session_state[SK.SHOW_RECIPE_DETAILS] = global_idx
                st.rerun()


def app_screen(df):
    st.markdown("#### Enter ingredients or a recipe name")

    query = st.text_input(
        "Ingredients or recipe",
        label_visibility="collapsed",
    )

    if st.button("Get Recommendations"):
        q = query.strip()
        if not q:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Building recipe index (first time only)…"):
                st.session_state[SK.RECOMMENDATION_DF] = recommend(df, q)
                st.session_state[SK.PAGE] = 1
                st.session_state[SK.SHOW_RECIPE_DETAILS] = None
            st.rerun()

    rec_df = st.session_state.get(SK.RECOMMENDATION_DF)
    if rec_df is None:
        return

    st.sidebar.header("Filters")

    cuisine = st.sidebar.selectbox(
        "Cuisine",
        ["Any"] + sorted(rec_df["Cuisine"].dropna().unique().tolist()),
    )

    course = st.sidebar.selectbox(
        "Course",
        ["Any"] + sorted(rec_df["Course"].dropna().unique().tolist()),
    )

    diet = st.sidebar.selectbox(
        "Diet",
        ["Any"] + sorted(rec_df["Diet"].dropna().unique().tolist()),
    )

    max_time = st.sidebar.slider(
        "Maximum time (minutes)",
        0,
        CONFIG.DEFAULT_MAX_TIME,
        CONFIG.DEFAULT_MAX_TIME,
    )

    if st.sidebar.button("Filter"):
        filtered = filter_recipes(rec_df, cuisine, course, diet, max_time)
        _display_results(filtered)
    else:
        _display_results(rec_df)