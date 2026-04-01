from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserPreferences(BaseModel):
    relaxing_activities: List[str] = []
    hobbies: List[str] = []
    stress_triggers: List[str] = []
    music_preferences: List[str] = []
    preferred_activities: List[str] = []
    disliked_environments: List[str] = []
    time_of_day_preference: Optional[str] = None

class EmotionCategory(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    STRESS = "stress"
    ANXIETY = "anxiety"
    CALM = "calm"
    EXCITEMENT = "excitement"

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    full_name: Optional[str] = None
    preferences: UserPreferences = UserPreferences()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    anonymous_mode: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    anonymous_mode: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    preferences: UserPreferences
    created_at: datetime
    is_active: bool
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    anonymous_mode: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
