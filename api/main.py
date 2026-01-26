from fastapi import FastAPI
from src.models.recette import init_db
import src.router.food_router as food_router
app = FastAPI()

app.include_router(food_router.router)

@app.get("/")
async def root():
    init_db()
    return {"message": "Hello World"}