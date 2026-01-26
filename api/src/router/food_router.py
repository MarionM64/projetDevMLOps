from fastapi import APIRouter, FastAPI

from src.services.food_service import get_recette_par_id, rechercher_recettes

router = APIRouter()


@router.get("/recette/", tags=["recette"])
async def afficheRecette(id):
    return get_recette_par_id(id)


@router.get("/recherche/recettes/", tags=["recherce"])
async def rechercheRecette(query):
    return rechercher_recettes(query)