from fastapi import FastAPI
import src.router.food_router as food_router
app = FastAPI()

app.include_router(food_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}