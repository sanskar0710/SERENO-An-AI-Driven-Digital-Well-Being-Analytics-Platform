from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import jwt
import hashlib
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

# Import routers
from routers import auth, journal, community, chat, suggestions, insights

# Database connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "sereno_db"

def get_database():
    return app.state.database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.state.database = app.state.mongodb_client[DATABASE_NAME]
    
    # Create indexes
    await app.state.database.users.create_index("email", unique=True)
    await app.state.database.journal_entries.create_index([("user_id", 1), ("timestamp", -1)])
    await app.state.database.community_posts.create_index([("timestamp", -1)])
    await app.state.database.chat_messages.create_index([("chat_id", 1), ("timestamp", 1)])
    
    yield
    
    # Shutdown
    app.state.mongodb_client.close()

app = FastAPI(
    title="Sereno API",
    description="AI-Driven Digital Well-Being & Community Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(community.router, prefix="/api/community", tags=["community"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["suggestions"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time messages here
            await manager.send_personal_message(f"Message received: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.get("/")
async def root():
    return {"message": "Welcome to Sereno API - AI-Driven Digital Well-Being Platform"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
