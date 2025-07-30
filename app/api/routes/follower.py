from fastapi import APIRouter
from typing import Annotated, List, Dict, Type

from fastapi.params import Body
from app.models.models import Users  , Follow

from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import get_db
from app.schema.schema import UserOut, UserBase
from app.repositories.user_repository import get_user_by_id
from app.repositories.follower_repository import get_follower, get_following

# following -- user that will be followed
# follower -- user that is following


router = APIRouter()


# follow a user
@router.post("/users/follow/")
async def follow_user(follower_id: Annotated[int , Body()], following_id: Annotated[int , Body()], db: Session = Depends(get_db)):
    try:
        new_follow = Follow(follower_id=follower_id, following_id=following_id)
        db.add(new_follow)
        db.commit()
        db.refresh(new_follow)
        return {"message": "Followed successfully", "follow": new_follow}
    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    

# get followers of a user
@router.get("/users/{user_id}/followers", response_model=List[UserBase])
async def get_followers(user_id: int, db: Session = Depends(get_db)):   
    followers = db.query(Follow).filter(Follow.following_id == user_id).all()
    follower_ids = [follower.follower_id for follower in followers]
    users = db.query(Users).filter(Users.id.in_(follower_ids)).all()
    return users

# get users that a user is following
@router.get("/users/{user_id}/following", response_model=List[UserBase])
async def get_followers(user_id: int, db: Session = Depends(get_db)):   
    following = db.query(Follow).filter(Follow.follower_id == user_id).all()
    following_ids = [following.follower_id for following in following]
    users = db.query(Users).filter(Users.id.in_(following_ids)).all()
    return users

