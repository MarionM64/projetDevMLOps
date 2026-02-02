from fastapi import APIRouter, FastAPI

from src.models.recipe import add_like_recipe, get_like_by_recipe
from src.services.food_service_spoonacular import research_recipe, get_recipe_by_id
from model.model import recommend_implicit

router = APIRouter()


@router.get("/recipe/{id}", tags=["recipe"])
async def getRecipe(id : int):
    res = get_recipe_by_id(id)
    if res != None :
        res["like"]= get_like_by_recipe(id)
    return res


@router.put("/recipe/like/{id}", tags=["recipe"])
async def likeRecipe(id : int):
    return add_like_recipe(id)

@router.get("/research/recipe/{query}", tags=["research"])
async def researchRecipe(query : str):
    return research_recipe(query)


@router.get("/recommend/recipe", tags=["recommend"])
async def recommendRecipe():
    res = recommend_implicit()

    return {"results": [get_recipe_by_id(id) for [id, _, _] in res]}

