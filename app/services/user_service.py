from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.repositories import user_repository, file_repository

def handle_profile_picture_upload(db: Session, user_id: int, file: UploadFile):
    filename = file_repository.save_file(user_id, file)
    return user_repository.update_profile_picture(db, user_id, filename)
