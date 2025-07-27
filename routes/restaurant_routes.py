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
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import Response

# Local modules
from database.db import SessionLocal, Base, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status
from utils.auth import verify_password, get_password_hash, create_access_token, get_current_user
from database.models import MenuItem, Restaurant, User, Menu, Category  # ORM models
from schemas.menu_item import MenuItemCreate, MenuItemOut
from schemas.restaurant import RestaurantCreate, RestaurantOut  # Pydantic schemas
from utils import crud  # Add CRUD functions for User model
from utils.ocr_extractor import run_ocr
from schemas.user import UserCreate, UserOut
from utils.grammar_ocr_food_parser import extract_menu_data
from utils.imagesearch import enrich_menu_with_images, fetch_image_links
from utils.parser import handle_parse_menu
from utils.enricher import enrich_menu_item
import traceback


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/parse_menu/", response_model=RestaurantOut)
async def parse_menu(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Step 1: Parse uploaded file to get restaurant + menu data dict
    parsed_data = await handle_parse_menu(file)
    restaurant_name = parsed_data.get("restaurant_name")

    if not restaurant_name:
        raise HTTPException(status_code=400, detail="Missing restaurant name in parsed data")

    # Step 2: Check if restaurant already exists by name
    existing_restaurant = db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if existing_restaurant:
        return existing_restaurant

    # Step 3: Create restaurant with menu in DB
    try:
        restaurant = crud.create_restaurant_with_menu(db, parsed_data)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DB insert failed: {str(e)}")

    # Step 4: Return the created restaurant object
    return restaurant

@router.post("/enrich_menu/")
async def enrich_menu(
    parsed_menu: Dict[str, Any] = Body(...),
    slug: str = Query(...),
    images_per_item: int = Query(1)
):
    return enrich_menu_item(parsed_menu, slug, images_per_item)




# Auth routes (no prefix)

@router.post("/signup", response_model=UserOut)
def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_create.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user_create.password)
    new_user = crud.create_user(db, email=user_create.email, hashed_password=hashed_pw)
    return new_user


@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    

@router.post("/logout")
def logout():
    # On frontend, just remove token from localStorage
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
