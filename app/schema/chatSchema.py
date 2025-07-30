from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Chat(BaseModel):
    room_id: int
    is_group: bool = False
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Message(BaseModel):
    message:str

class MessageSchema(Message):
    user_id: int
    room_id: str
    timestamp: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)