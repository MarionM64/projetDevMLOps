from fastapi import FastAPI
from src.models.recipe import init_db
import src.router.food_router as food_router
app = FastAPI()

app.include_router(food_router.router)

try:
    init_db()
except Exception as e:
    print(f"Erreur lors de l'initialisation: {e}")

@app.get("/")
async def root():
    print("ok")
    return {"message": "Hello World"}