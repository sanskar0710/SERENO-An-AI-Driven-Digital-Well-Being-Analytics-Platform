from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.user import EmotionCategory

class EmotionAnalysis(BaseModel):
    emotion: EmotionCategory
    confidence: float = Field(ge=0.0, le=1.0)
    key_words: List[str] = []
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    intensity: str = Field(default="moderate", regex="^(low|moderate|high)$")

class JournalEntry(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis: Optional[EmotionAnalysis] = None
    mood_rating: Optional[int] = Field(None, ge=1, le=10)
    tags: List[str] = []
    is_private: bool = True
    media_files: List[str] = []
    
class JournalEntryCreate(BaseModel):
    text: str
    mood_rating: Optional[int] = Field(None, ge=1, le=10)
    tags: List[str] = []
    is_private: bool = True

class JournalEntryUpdate(BaseModel):
    text: Optional[str] = None
    mood_rating: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None

class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    text: str
    timestamp: datetime
    analysis: Optional[EmotionAnalysis] = None
    mood_rating: Optional[int] = None
    tags: List[str] = []
    is_private: bool
    media_files: List[str] = []

class TextAnalysisRequest(BaseModel):
    text: str
    user_preferences: Optional[Dict[str, Any]] = None

class TextAnalysisResponse(BaseModel):
    emotion: EmotionCategory
    confidence: float
    key_words: List[str]
    sentiment_score: float
    intensity: str
    insights: List[str] = []
    suggestions: List[str] = []
