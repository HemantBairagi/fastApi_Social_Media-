from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- ENUMS ---
class PostType(str, Enum):
    text = "text"
    image = "image"
    video = "video"


class CommentType(str, Enum):
    GIF = "GIF"
    TEXT = "TEXT"


# --- Base Schemas ---
class UserBase(BaseModel):
    id : int
    name: str  
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    bio: Optional[str] = "."
    is_active: Optional[bool] = True
    is_online: Optional[bool] = False
    model_config = ConfigDict(from_attributes=True)

  

# --- Post Schemas ---
class PostBase(BaseModel):
    id: int
    post_type: PostType
    post_text: Optional[str] = None

class PostCreate(PostBase):
    user_id: int

class PostOut(PostBase):
    user_id: int
    likes: int = 0
    created_at: datetime = datetime.now()
    model_config = ConfigDict(from_attributes=True)


# --- Comment Schemas ---
class CommentBase(BaseModel):
    comment_type: CommentType
    comment: str

class CommentCreate(CommentBase):
    user_id: int
    post_id: int

class CommentOut(CommentBase):
    id: int
    user_id: int
    post_id: int
    likes: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Like Schema ---
class LikeSchema(BaseModel):
    user_id: int
    post_id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Follow Schema ---
class FollowSchema(BaseModel):
    follower_id: int
    following_id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

