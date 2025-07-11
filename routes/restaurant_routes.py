# Standard library
import json
import shutil
from datetime import datetime
from os import makedirs
from typing import Any, Dict

# Third-party packages
from fastapi import (
    APIRouter, Depends, HTTPException, FastAPI, File, UploadFile, Body, Query
)
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from sqlalchemy.orm import Session

# Local modules
from database.db import SessionLocal, Base, engine
from database.models import MenuItem, MenuItemCreate, MenuItemOut
from database.models import Restaurant
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status
from utils.auth import verify_password, get_password_hash, create_access_token
from database.models import User, UserCreate, UserOut
from utils import crud  # Add CRUD functions for User model
from utils.ocr_extractor import run_ocr
from utils.grammar_ocr_food_parser import extract_menu_data
from utils.imagesearch import enrich_menu_with_images, fetch_image_links
from utils.parser import handle_parse_menu
from utils.enricher import enrich_menu_item

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()

@router.post("/parse_menu/")
async def parse_menu(file: UploadFile = File(...)):
    return await handle_parse_menu(file)

@router.post("/enrich_menu/")
async def enrich_menu(
    parsed_menu: Dict[str, Any] = Body(...),
    slug: str = Query(...),
    images_per_item: int = Query(1)
):
    return enrich_menu_item(parsed_menu, slug, images_per_item)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=MenuItemOut)
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    return crud.create_object(db, MenuItem, item.dict())

@router.get("/", response_model=list[MenuItemOut])
def get_all_menu_items(db: Session = Depends(get_db)):
    return crud.get_all(db, MenuItem)

@router.get("/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_one(db, MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}")
def update_menu_item(item_id: str, update: dict, db: Session = Depends(get_db)):
    item = crud.update_object(db, MenuItem, item_id, update)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@router.delete("/{item_id}")
def delete_menu_item(item_id: str, db: Session = Depends(get_db)):
    success = crud.delete_object(db, MenuItem, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}



@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = crud.create_user(db, email=user.email, hashed_password=hashed_pw)
    return new_user

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# Dependency to get current user
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user