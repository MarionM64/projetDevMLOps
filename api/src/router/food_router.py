from fastapi import APIRouter, FastAPI

from src.models.recipe import add_like_recipe
from src.services.food_service_spoonacular import research_recipe, get_recipe_by_id

router = APIRouter()


@router.get("/recipe/{id}", tags=["recipe"])
async def getRecipe(id : int):
    return get_recipe_by_id(id)


@router.get("/recipe/like/{id}", tags=["recipe"])
async def likeRecipe(id : int):
    return add_like_recipe(id)

@router.get("/research/recipe/{query}", tags=["research"])
async def researchRecipe(query : str):
    return research_recipe(query)

