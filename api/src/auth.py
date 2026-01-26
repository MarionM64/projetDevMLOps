from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt, JWTError
from pydantic import BaseModel
import model
import config
import auth_router



# Crée un routeur dédié à l’authentification
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Déclaration du schéma OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")



@router.post("/token", response_model=model.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    # Exemple : utilisateur "peio" avec mot de passe "123"
    for username, user in model.default_users.items():
        if form_data.username == username and form_data.password == user.password:
            # Création du token JWT
            access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = auth_router.create_access_token(
                data={"sub": form_data.username}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
    )

    



@router.get("/protected")
async def protected(current_user: model.Token = Depends(get_current_user)):
    """
    Exemple de route protégée : nécessite un token JWT valide.
    """
    return {"message": "Authentifié avec succès", "user": current_user}


