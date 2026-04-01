from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import json

from models import User
from main import get_database, manager
from routers.auth import get_current_user

router = APIRouter()

# WebSocket connection manager extended for chat
class ChatConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, str] = {}  # connection_id -> user_id

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.user_connections[connection_id] = user_id
        
        return connection_id

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from user_connections
        to_remove = [conn_id for conn_id, uid in self.user_connections.items() if uid == user_id]
        for conn_id in to_remove:
            del self.user_connections[conn_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(json.dumps(message))

    async def send_chat_message(self, message: dict, sender_id: str, receiver_id: str):
        # Send to receiver
        await self.send_personal_message(message, receiver_id)
        # Send to sender for confirmation
        await self.send_personal_message(message, sender_id)

chat_manager = ChatConnectionManager()

@router.websocket("/chat/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    connection_id = await chat_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "chat_message":
                await handle_chat_message(message_data, user_id)
            elif message_data.get("type") == "typing":
                await handle_typing_indicator(message_data, user_id)
            elif message_data.get("type") == "read_receipt":
                await handle_read_receipt(message_data, user_id)
                
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, user_id)

async def handle_chat_message(message_data: dict, sender_id: str):
    """Handle chat message and save to database"""
    from main import get_database
    
    db = get_database()
    receiver_id = message_data.get("receiver_id")
    
    if not receiver_id:
        return
    
    # Save message to database
    message_dict = {
        "id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message_data.get("message"),
        "timestamp": datetime.utcnow(),
        "is_read": False,
        "message_type": message_data.get("message_type", "text"),
        "media_url": message_data.get("media_url"),
        "reply_to": message_data.get("reply_to")
    }
    
    await db.chat_messages.insert_one(message_dict)
    
    # Send to both users
    await chat_manager.send_chat_message({
        "type": "new_message",
        "message": message_dict
    }, sender_id, receiver_id)

async def handle_typing_indicator(message_data: dict, sender_id: str):
    """Handle typing indicator"""
    receiver_id = message_data.get("receiver_id")
    
    if receiver_id:
        await chat_manager.send_personal_message({
            "type": "typing",
            "sender_id": sender_id,
            "is_typing": message_data.get("is_typing", False)
        }, receiver_id)

async def handle_read_receipt(message_data: dict, user_id: str):
    """Handle read receipt"""
    from main import get_database
    
    db = get_database()
    message_id = message_data.get("message_id")
    
    if message_id:
        # Mark message as read
        await db.chat_messages.update_one(
            {"id": message_id, "receiver_id": user_id},
            {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
        )

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all conversations for the current user"""
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"sender_id": current_user.id},
                    {"receiver_id": current_user.id}
                ]
            }
        },
        {
            "$group": {
                "_id": {
                    "$cond": {
                        "if": {"$eq": ["$sender_id", current_user.id]},
                        "then": "$receiver_id",
                        "else": "$sender_id"
                    }
                },
                "last_message": {"$last": "$message"},
                "last_timestamp": {"$last": "$timestamp"},
                "unread_count": {
                    "$sum": {
                        "$cond": {
                            "if": {
                                "$and": [
                                    {"$eq": ["$receiver_id", current_user.id]},
                                    {"$eq": ["$is_read", False]}
                                ]
                            },
                            "then": 1,
                            "else": 0
                        }
                    }
                }
            }
        },
        {"$sort": {"last_timestamp": -1}}
    ]
    
    conversations = await db.chat_messages.aggregate(pipeline).to_list(length=None)
    
    # Get user details for each conversation
    result = []
    for conv in conversations:
        other_user_id = conv["_id"]
        user_data = await db.users.find_one({"_id": other_user_id})
        
        if user_data:
            result.append({
                "user_id": other_user_id,
                "username": user_data.get("username"),
                "full_name": user_data.get("full_name"),
                "profile_picture": user_data.get("profile_picture"),
                "last_message": conv["last_message"],
                "last_timestamp": conv["last_timestamp"],
                "unread_count": conv["unread_count"]
            })
    
    return result

@router.get("/messages/{other_user_id}")
async def get_chat_messages(
    other_user_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get chat messages between current user and another user"""
    messages = await db.chat_messages.find({
        "$or": [
            {"sender_id": current_user.id, "receiver_id": other_user_id},
            {"sender_id": other_user_id, "receiver_id": current_user.id}
        ]
    }).sort("timestamp", -1).skip(offset).limit(limit).to_list(length=limit)
    
    # Mark messages as read
    await db.chat_messages.update_many(
        {
            "sender_id": other_user_id,
            "receiver_id": current_user.id,
            "is_read": False
        },
        {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
    )
    
    return list(reversed(messages))

@router.post("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark a specific message as read"""
    result = await db.chat_messages.update_one(
        {
            "id": message_id,
            "receiver_id": current_user.id
        },
        {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return {"message": "Message marked as read"}

@router.get("/online-users")
async def get_online_users(current_user: User = Depends(get_current_user)):
    """Get list of online users"""
    online_users = list(chat_manager.active_connections.keys())
    return {"online_users": [uid for uid in online_users if uid != current_user.id]}
