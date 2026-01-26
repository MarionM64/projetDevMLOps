from fastapi import APIRouter, FastAPI

from src.services.food_service import get_recette_par_id, rechercher_recettes, get_affichage_recette_par_id

router = APIRouter()


@router.get("/recette/{id}", tags=["recette"])
async def afficheRecette(id : int):
    return get_affichage_recette_par_id(id)


@router.get("/recherche/recettes/{query}", tags=["recherce"])
async def rechercheRecette(query : str):
    return rechercher_recettes(query)