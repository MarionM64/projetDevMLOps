from fastapi import APIRouter, FastAPI

from src.services.food_service import research_recipe, get_recipe_by_id, get_card_recipe_by_id

router = APIRouter()


@router.get("/recipe/{id}", tags=["recipe"])
async def afficheRecette(id : int):
    return get_recipe_by_id(id)


@router.get("/research/recipe/{query}", tags=["research"])
async def rechercheRecette(query : str):
    return research_recipe(query)