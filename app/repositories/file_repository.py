import os, shutil
from fastapi import UploadFile

BASE_UPLOAD_PATH = "uploads"

def save_file(user_id: int, file: UploadFile) -> str:
    user_dir = os.path.join(BASE_UPLOAD_PATH, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file.filename
