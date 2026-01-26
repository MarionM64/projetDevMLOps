from dotenv import load_dotenv
import os
import requests

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API
API_KEY = os.getenv("API_FOOD_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"

def rechercher_recettes(query):
    endpoint = f"{BASE_URL}/complexSearch"
    params = {
        "apiKey": API_KEY,
        "query": query,
        'number': 10
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None


def get_recette_par_id(id_recette):
    endpoint = f"{BASE_URL}/{id_recette}/information"
    params = {
        "apiKey": API_KEY,
        "includeNutrition": False
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None
    

def get_affichage_recette_par_id(id_recette):
    endpoint = f"{BASE_URL}/{id_recette}/card"
    params = {
        "apiKey": API_KEY,
        "id": id_recette,
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None
    
