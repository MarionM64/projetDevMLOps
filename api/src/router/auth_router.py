from fastapi import FastAPI, HTTPException, Depends, APIRouter
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError

import model
import config

router = APIRouter()


#fonction relative a l'authentification et a la gestion des tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

def refresh_access_token(token: str, expires_delta: Optional[timedelta] = None):
    try:
        clejwt = jwt.decode(token, config.settings.KEY, algorithms=[config.settings.ALGORITHM])
        username: str = clejwt.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = model.TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    new_token = create_access_token(data={"sub": token_data.username}, expires_delta=expires_delta)
    return {"access_token": new_token, "token_type": "bearer"}

