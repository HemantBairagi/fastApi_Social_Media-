from fastapi import APIRouter 
from typing import List
from app.models.models import Users
from sqlalchemy.orm import Session
from fastapi import Depends, UploadFile, File
from app.services.user_service import handle_profile_picture_upload
from app.db.database import get_db
from app.models.models import Users as User
from app.schema.schema import UserOut , UserBase
from app.repositories.user_repository import get_user_by_id
from app.repositories.follower_repository import get_follower, get_following

router = APIRouter()



# ✅ Use Pydantic model as input
@router.post("/users", response_model=UserOut)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        bio=user.bio,
        is_active=user.is_active,
        is_online=user.is_online,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        return {"error": "User not found"}
    return {
     "user":db_user
    }


@router.post("/users/{user_id}/upload-profile", response_model=UserOut)
def upload_profile_picture(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    handle_profile_picture_upload(db, user_id, file)
    user = get_user_by_id(db, user_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profile_picture": f"/media/user_{user_id}/{user.profile_picture}" if user.profile_picture else None
    }


@router.get("/users/{user_id}/profile-picture")
def get_profile_picture(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user or not user.profile_picture:
        return {"error": "Profile picture not found"}
    return {
        "profile_picture": f"/media/user_{user_id}/{user.profile_picture}"
    }




