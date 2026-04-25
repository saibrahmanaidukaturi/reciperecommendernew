from app.data.repository import load_recipes
from app.ml.recommender import recommend


def get_recommendations(query: str, top_k: int) -> list[dict]:
    df = load_recipes()
    recs = recommend(query, df=df, top_k=top_k)

    results: list[dict] = []
    for _, row in recs.iterrows():
        results.append(
            {
                "recipe_name": str(row.get("RecipeName", "")),
                "ingredients": str(row.get("Ingredients", "")),
                "total_time_mins": int(row.get("TotalTimeInMins", 0) or 0),
                "cuisine": str(row.get("Cuisine", "")),
                "course": str(row.get("Course", "")),
                "diet": str(row.get("Diet", "")),
                "instructions": str(row.get("Instructions", "")),
                "url": str(row.get("URL", "")),
            }
        )

    return results
