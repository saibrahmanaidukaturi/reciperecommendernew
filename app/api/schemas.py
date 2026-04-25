from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=12, ge=1, le=50)


class RecipeOut(BaseModel):
    recipe_name: str
    ingredients: str
    total_time_mins: int
    cuisine: str
    course: str
    diet: str
    instructions: str
    url: str


class RecommendResponse(BaseModel):
    query: str
    results: list[RecipeOut]
