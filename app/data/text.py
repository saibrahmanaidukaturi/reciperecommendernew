import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def build_combined_text(df: pd.DataFrame) -> pd.Series:
    combined = (
        df["RecipeName"].astype(str) + " "
        + df["Ingredients"].astype(str) + " "
        + df["TotalTimeInMins"].astype(str) + " "
        + df["Cuisine"].astype(str) + " "
        + df["Course"].astype(str) + " "
        + df["Diet"].astype(str)
    )

    return combined.fillna("").str.lower()  