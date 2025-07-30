# ======================= WebSocket Management =======================

from typing import Dict, List
import uuid
from fastapi import APIRouter, Depends, HTTPException ,WebSocket, WebSocketDisconnect
from sqlalchemy import UUID
from app.models.models import Conversations , ConversationParticipants, Messages , Users
from app.schema.chatSchema import Chat, Message, MessageSchema
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

# Store active WebSocket connections per chat room
connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, user_id: int, db: Session = Depends(get_db)):
    await websocket.accept()

    if chat_id not in connections:
        connections[chat_id] = []
    connections[chat_id].append(websocket)

    user = db.query(Users).filter(Users.id == user_id).first()
    user_name = user.name if user else f"User-{user_id}"

    try:
        while True:
            data = await websocket.receive_text()

            # ✅ Save to database
            new_msg = Messages(
                room_id=chat_id,
                sender_id=user_id,
                content=data
            )
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)

            # ✅ Broadcast to all clients in this chat
            for client in connections[chat_id]:
                await client.send_text(f"{user_name}: {data}")
                await client.send_json({
                    "message_id": str(new_msg.message_id),
                    "room_id": str(chat_id),
                    "sender_id": user_id,
                    "sender_name": user_name,
                    "content": data,
                    "sent_at": new_msg.sent_at.isoformat()
                })

    except WebSocketDisconnect:
        connections[chat_id].remove(websocket)


# ======================= Chat Endpoints =======================

@router.get("/chat/{user_id}")
async def get_chat(user_id: int, db: Session = Depends(get_db)):
    chat = db.query(Conversations).filter(Conversations.creator_id == user_id).all()
    if chat:
        return chat
    return {"message": f"Chat for user {user_id} is not implemented yet."}


@router.get("/chat/{user_id}/{chat_id}")
async def get_chat_by_id(user_id: int, chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(ConversationParticipants).filter(
        ConversationParticipants.user_id == user_id, ConversationParticipants.room_id == chat_id
    ).first()
    if chat:
        return chat
    return {"message": f"Chat with ID {chat_id} for user {user_id} not found."}


@router.post("/chat/{user_id}")
async def create_chat(user_id: int, chat: Chat, db: Session = Depends(get_db)):
    new_chat = Conversations(
        creator_id=user_id,
        title=chat.name,
        is_group=chat.is_group,
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    participant = ConversationParticipants(
        user_id=user_id,
        room_id=new_chat.id
    )
    db.add(participant)
    db.commit()
    return {"message": "Chat created successfully", "chat_id": new_chat.id}


@router.post("/chat/{user_id}/{chat_id}/send-message")
async def send_message(
    user_id: int,
    chat_id: str,
    message_data: Message,
    db: Session = Depends(get_db)
):
    participant = db.query(ConversationParticipants).filter(
        ConversationParticipants.user_id == user_id,
        ConversationParticipants.room_id == chat_id
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="User is not a participant.")

    new_message = Messages(
        room_id=chat_id,
        sender_id=user_id,
        content=message_data.message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {
        "message_id": str(new_message.message_id),
        "room_id": str(new_message.room_id),
        "sender_id": new_message.sender_id,
        "content": new_message.content,
        "sent_at": new_message.sent_at.isoformat()
    }


@router.get("/chat/{chat_id}/get-message/")
async def get_messages(
    chat_id: str,
    db: Session = Depends(get_db)
):
    participant = db.query(ConversationParticipants).filter(
        ConversationParticipants.room_id == chat_id
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="User is not a participant.")

    messages = db.query(Messages).filter(Messages.room_id == chat_id).order_by(Messages.sent_at).all()

    if not messages:
        return {"message": "No messages found in this chat."}

    return [MessageSchema(
        user_id=msg.sender_id,
        room_id=str(msg.room_id),
        message=msg.content,
        timestamp=msg.sent_at
    ) for msg in messages]


@router.get("/chat/{chat_id}/participants")
async def get_chat_participants(
    chat_id: str,
    db: Session = Depends(get_db)
):
    try:
        participants = db.query(ConversationParticipants).filter(ConversationParticipants.room_id == chat_id).all()

        if not participants:
            return {"message": "No participants found in this chat."}

        return [{"user_id": participant.user_id, "room_id": str(participant.room_id)} for participant in participants]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

