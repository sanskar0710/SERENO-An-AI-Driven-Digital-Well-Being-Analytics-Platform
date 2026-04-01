from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReactionType(str, Enum):
    LIKE = "like"
    LOVE = "love"
    SUPPORT = "support"
    INSPIRED = "inspired"
    GRATEFUL = "grateful"

class Comment(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    username: str
    anonymous: bool = False
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reactions: Dict[str, int] = {}
    is_edited: bool = False
    edited_at: Optional[datetime] = None

class CommunityPost(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    username: str
    anonymous: bool = False
    title: Optional[str] = None
    text: str
    media_files: List[str] = []
    tags: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reactions: Dict[str, int] = {}
    comments: List[Comment] = []
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_moderated: bool = False
    moderation_reason: Optional[str] = None

class CommunityPostCreate(BaseModel):
    title: Optional[str] = None
    text: str
    anonymous: bool = False
    tags: List[str] = []

class CommunityPostUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    tags: Optional[List[str]] = None
    anonymous: Optional[bool] = None

class CommentCreate(BaseModel):
    text: str
    anonymous: bool = False

class CommentUpdate(BaseModel):
    text: str

class CommunityPostResponse(BaseModel):
    id: str
    user_id: str
    username: str
    anonymous: bool
    title: Optional[str] = None
    text: str
    media_files: List[str] = []
    tags: List[str] = []
    timestamp: datetime
    reactions: Dict[str, int] = {}
    comments: List[Comment] = []
    is_edited: bool = False
    edited_at: Optional[datetime] = None

class ReactionCreate(BaseModel):
    reaction_type: ReactionType
