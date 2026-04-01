from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from models import (
    JournalEntry, JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse,
    TextAnalysisRequest, TextAnalysisResponse, EmotionAnalysis, User
)
from main import get_database
from routers.auth import get_current_user
from services.ai_analyzer import AIAnalyzer

router = APIRouter()
ai_analyzer = AIAnalyzer()

@router.post("/entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Analyze the text using AI
    analysis = await ai_analyzer.analyze_text(entry.text, current_user.preferences.dict())
    
    entry_dict = entry.dict()
    entry_dict["user_id"] = current_user.id
    entry_dict["_id"] = str(uuid.uuid4())
    entry_dict["timestamp"] = datetime.utcnow()
    entry_dict["analysis"] = analysis.dict()
    
    result = await db.journal_entries.insert_one(entry_dict)
    created_entry = await db.journal_entries.find_one({"_id": result.inserted_id})
    
    return JournalEntryResponse(**created_entry)

@router.get("/entries", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    entries = await db.journal_entries.find(
        {"user_id": current_user.id}
    ).sort("timestamp", -1).skip(offset).limit(limit).to_list(length=limit)
    
    return [JournalEntryResponse(**entry) for entry in entries]

@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    entry = await db.journal_entries.find_one({
        "_id": entry_id,
        "user_id": current_user.id
    })
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return JournalEntryResponse(**entry)

@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_update: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Check if entry exists and belongs to user
    existing_entry = await db.journal_entries.find_one({
        "_id": entry_id,
        "user_id": current_user.id
    })
    
    if not existing_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    update_data = entry_update.dict(exclude_unset=True)
    
    # Re-analyze text if it was updated
    if "text" in update_data:
        analysis = await ai_analyzer.analyze_text(update_data["text"], current_user.preferences.dict())
        update_data["analysis"] = analysis.dict()
    
    await db.journal_entries.update_one(
        {"_id": entry_id},
        {"$set": update_data}
    )
    
    updated_entry = await db.journal_entries.find_one({"_id": entry_id})
    return JournalEntryResponse(**updated_entry)

@router.delete("/entries/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    result = await db.journal_entries.delete_one({
        "_id": entry_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return {"message": "Journal entry deleted successfully"}

@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    analysis = await ai_analyzer.analyze_text(request.text, request.user_preferences or current_user.preferences.dict())
    return analysis

@router.get("/stats")
async def get_journal_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Get emotion distribution
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": "$analysis.emotion",
            "count": {"$sum": 1}
        }}
    ]
    
    emotion_stats = await db.journal_entries.aggregate(pipeline).to_list(length=None)
    
    # Get mood trends
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    mood_pipeline = [
        {"$match": {
            "user_id": current_user.id,
            "timestamp": {"$gte": thirty_days_ago}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "avg_mood": {"$avg": "$mood_rating"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    mood_trends = await db.journal_entries.aggregate(mood_pipeline).to_list(length=None)
    
    # Get total entries count
    total_entries = await db.journal_entries.count_documents({"user_id": current_user.id})
    
    return {
        "emotion_distribution": emotion_stats,
        "mood_trends": mood_trends,
        "total_entries": total_entries
    }
