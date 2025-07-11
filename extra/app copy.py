from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
from PIL import Image
from ocr_extractor import run_ocr
from grammar_ocr_food_parser import extract_menu_data
from imagesearch import enrich_menu_with_images, fetch_image_links
from os import makedirs

app = FastAPI()

# Allow all CORS (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_menu/")
async def upload_image(file: UploadFile = File(...)):
    # Ensure 'temp' directory exists
    makedirs("temp", exist_ok=True)

    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process image (e.g., extract text, classify, etc.)
    img = Image.open(temp_path)
    
    # Extract Text from Image
    raw_menu_data = run_ocr(temp_path)

    print(raw_menu_data)

    raw_text = "\n".join(item['text'] for item in raw_menu_data)  # join list elements into one string

    # Grammar Correct And Parse

    parsed_menu_data = extract_menu_data(raw_text)

    # Fetch and Attach dish image URLs

    final_menu_data = enrich_menu_with_images(parsed_menu_data)

    return final_menu_data

