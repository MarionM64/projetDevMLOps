from dotenv import load_dotenv
import os
import requests

from src.models.recette import add_like_recipe, add_recipe

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API
API_KEY = os.getenv("API_FOOD_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"

def research_recipe(query):
    endpoint = f"{BASE_URL}/complexSearch"
    params = {
        "apiKey": API_KEY,
        "query": query,
        'number': 30
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        res = response.json()
        for recipe in res["results"]:
            add_recipe(recipe)
        return res
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None


def get_recipe_by_id(id_recipe):
    endpoint = f"{BASE_URL}/{id_recipe}/information"
    params = {
        "apiKey": API_KEY,
        "includeNutrition": False
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        add_like_recipe(id_recipe)
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None
    

def get_card_recipe_by_id(id_recipe):
    endpoint = f"{BASE_URL}/{id_recipe}/card"
    params = {
        "apiKey": API_KEY,
        "id": id_recipe,
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None
    
