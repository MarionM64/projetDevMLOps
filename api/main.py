from fastapi import FastAPI
import src.router.food_router as food_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(food_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}