from fastapi import APIRouter, FastAPI, HTTPException
from prometheus_client import Counter
from src.models.recipe import add_like_recipe, get_like_by_recipe
from src.services.food_service_spoonacular import research_recipe, get_recipe_by_id
from model.model import recommend_implicit

router = APIRouter()

recipe_track_total_like = Counter(
    "recipe_track_total_like", 
    "Total des likes sur les recettes",
)

recipe_api_counter = Counter(
    "recipe_api_research_total",
    "Historique des recherches de recettes effectuées par l'API Spoonacular",
)

recipe_404_counter = Counter(
    "recipe_get_id_404_total",
    "Nombre de recettes non trouvées",
)

@router.get("/recipe/{id}", tags=["recipe"])
async def getRecipe(id: int):
    # call service synchronously; service returns None if recipe not found
    res = get_recipe_by_id(id)
    if res is None:
        recipe_404_counter.inc()
        raise HTTPException(status_code=404, detail=f"Recette {id} non trouvée")
    res["like"] = get_like_by_recipe(id)
    recipe_api_counter.inc()
    return res



@router.put("/recipe/like/{id}", tags=["recipe"])
async def likeRecipe(id : int):
    recipe_track_total_like.inc()
    return add_like_recipe(id)

@router.get("/research/recipe/{query}", tags=["research"])
async def researchRecipe(query : str):
    recipe_api_counter.inc(30)
    return research_recipe(query)


@router.get("/recommend/recipe", tags=["recommend"])
async def recommendRecipe():
    return recommend_implicit()

