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
from utils import crud
from utils.ocr_extractor import run_ocr
from utils.grammar_ocr_food_parser import extract_menu_data
from utils.imagesearch import enrich_menu_with_images, fetch_image_links
from utils.parser import handle_parse_menu
from utils.enricher import enrich_menu_item

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
