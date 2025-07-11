# utils/helpers.py

import os
import shutil
import json
from datetime import datetime
from fastapi import UploadFile

def save_uploaded_file(file: UploadFile, save_dir: str = "temp") -> str:
    os.makedirs(save_dir, exist_ok=True)
    temp_path = f"{save_dir}/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return temp_path

def save_json(data: dict, filename_prefix: str, save_dir: str = "saved") -> None:
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_dir}/{filename_prefix}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
