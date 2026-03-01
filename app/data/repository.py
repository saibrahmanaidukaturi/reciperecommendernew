import os
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_recipes() -> pd.DataFrame:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(base_dir, "data", "food.csv")

    df = pd.read_csv(csv_path)

    required_cols = [
        "RecipeName",
        "Ingredients",
        "TotalTimeInMins",
        "Cuisine",
        "Course",
        "Diet",
        "Instructions",
        "URL",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df["TotalTimeInMins"] = (
        pd.to_numeric(df["TotalTimeInMins"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return df