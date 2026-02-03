from fastapi import FastAPI
from model.tests.model import entrainement_modele
from src.services.food_service_spoonacular import research_recipe
from src.models.recipe import init_db
import src.router.food_router as food_router
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(food_router.router)

try:
    init_db()
    research_recipe("pasta")
except Exception as e:
    print(f"Erreur lors de l'initialisation: {e}")

@app.get("/")
async def root():
    print("ok")
    return {"message": "Hello World"}


Instrumentator().instrument(app).expose(app)