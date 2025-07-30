import uuid
from sqlalchemy import Column, Integer, String, Boolean, Text, Enum, ForeignKey, BigInteger, TIMESTAMP, Table , UUID
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime
from app.models.models import User

class Conversation(declarative_base()):
    __tablename__ = 'conversations'
    room_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    is_group = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

