from PIL import Image
from utils.ocr_extractor import run_ocr
from utils.grammar_ocr_food_parser import extract_menu_data
from utils.helpers import save_uploaded_file, save_json
from fastapi import UploadFile

async def handle_parse_menu(file: UploadFile) -> dict:
    image_path = save_uploaded_file(file)
    Image.open(image_path)  # just to validate it's an image

    raw_menu_data = run_ocr(image_path)
    raw_text = "\n".join(item['text'] for item in raw_menu_data)

    parsed_menu = extract_menu_data(raw_text)
    save_json(parsed_menu, "parsed_menu")

    return parsed_menu
