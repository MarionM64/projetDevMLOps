from fastapi import APIRouter
import model


router = APIRouter()

#fonctions CRUD user
@router.post("/user/create", tags=["users"])
async def create_user(user: model.User):
    # Dummy implementation for demonstration purposes
    return user

@router.put("/user/update/{user_id}", tags=["users"])
async def update_user(username: str):
    # Dummy implementation for demonstration purposes
    return {"username": username, "status": "updated"}

@router.delete("/user/delete/{user_id}", tags=["users"])
async def delete_user(username: str):
    # Dummy implementation for demonstration purposes
    return {"username": username, "status": "deleted"}


@router.get("/user/{user_id}", tags=["users"])
async def get_user(username: str):
    # Dummy implementation for demonstration purposes
    return {"username": username}
