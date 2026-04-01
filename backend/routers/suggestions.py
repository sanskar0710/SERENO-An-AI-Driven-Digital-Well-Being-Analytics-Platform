from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from models import User
from main import get_database
from routers.auth import get_current_user
from services.ai_analyzer import AIAnalyzer

router = APIRouter()
ai_analyzer = AIAnalyzer()

# Suggestion templates based on emotions and preferences
SUGGESTION_TEMPLATES = {
    "stress": [
        "Take a 5-minute break and practice deep breathing exercises.",
        "Go for a short walk to clear your mind.",
        "Listen to calming music or nature sounds.",
        "Try progressive muscle relaxation techniques.",
        "Write down your thoughts to gain perspective.",
        "Consider talking to a friend about what's bothering you."
    ],
    "sadness": [
        "Reach out to a friend or family member for support.",
        "Engage in an activity you usually enjoy.",
        "Watch a comforting movie or show.",
        "Spend time in nature if possible.",
        "Practice gratitude by listing three things you're thankful for.",
        "Consider creative expression like drawing or writing."
    ],
    "anxiety": [
        "Practice the 5-4-3-2-1 grounding technique.",
        "Try mindfulness meditation for 10 minutes.",
        "Challenge anxious thoughts by questioning their validity.",
        "Use positive self-talk and affirmations.",
        "Exercise to release tension and endorphins.",
        "Limit caffeine and screen time before bed."
    ],
    "joy": [
        "Savor this positive moment and what led to it.",
        "Share your joy with someone you care about.",
        "Write down what made you happy to revisit later.",
        "Plan more activities that bring you this feeling.",
        "Express gratitude for the positive experience.",
        "Consider helping others to spread the positivity."
    ],
    "anger": [
        "Take a few deep breaths before responding.",
        "Remove yourself from the situation temporarily.",
        "Express your feelings through physical activity.",
        "Practice assertive communication techniques.",
        "Consider the other person's perspective.",
        "Use relaxation techniques to calm your nervous system."
    ]
}

# Activity suggestions based on user preferences
ACTIVITY_SUGGESTIONS = {
    "music": [
        "Create a playlist of your favorite uplifting songs.",
        "Listen to a new album or artist you haven't explored.",
        "Try a guided meditation with calming background music.",
        "Attend a virtual concert or live stream performance."
    ],
    "walking": [
        "Take a 30-minute walk in a nearby park.",
        "Explore a new neighborhood on foot.",
        "Try a walking meditation or mindful walking practice.",
        "Join a local walking group or community."
    ],
    "reading": [
        "Start a new book in a genre you love.",
        "Visit your local library or bookstore.",
        "Join an online book club or reading community.",
        "Try reading poetry or inspirational quotes."
    ],
    "gaming": [
        "Play a relaxing or creative game.",
        "Join an online gaming community.",
        "Try a new game genre you haven't explored.",
        "Take breaks to stretch and rest your eyes."
    ],
    "cooking": [
        "Try a new recipe you've been curious about.",
        "Cook a comforting meal from your childhood.",
        "Experiment with baking or dessert making.",
        "Join a virtual cooking class or tutorial."
    ]
}

@router.get("/personalized")
async def get_personalized_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get personalized suggestions based on recent emotions and preferences"""
    
    # Get user's recent journal entries
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_entries = await db.journal_entries.find({
        "user_id": current_user.id,
        "timestamp": {"$gte": seven_days_ago}
    }).sort("timestamp", -1).limit(5).to_list(length=5)
    
    if not recent_entries:
        # No recent entries, provide general suggestions
        return get_general_suggestions(current_user.preferences.dict())
    
    # Analyze most recent emotion
    latest_entry = recent_entries[0]
    emotion = latest_entry.get("analysis", {}).get("emotion", "calm")
    
    # Get emotion-based suggestions
    emotion_suggestions = SUGGESTION_TEMPLATES.get(emotion, SUGGESTION_TEMPLATES["stress"])
    
    # Get preference-based suggestions
    preference_suggestions = get_preference_based_suggestions(current_user.preferences.dict())
    
    # Combine and randomize suggestions
    all_suggestions = emotion_suggestions + preference_suggestions
    random.shuffle(all_suggestions)
    
    return {
        "suggestions": all_suggestions[:6],  # Return top 6 suggestions
        "based_on": {
            "recent_emotion": emotion,
            "preferences": list(current_user.preferences.dict().keys())
        },
        "insight": get_emotion_insight(emotion, recent_entries)
    }

def get_preference_based_suggestions(preferences: Dict[str, Any]) -> List[str]:
    """Get suggestions based on user preferences"""
    suggestions = []
    
    # Check relaxing activities
    relaxing_activities = preferences.get("relaxing_activities", [])
    for activity in relaxing_activities:
        if activity.lower() in ACTIVITY_SUGGESTIONS:
            suggestions.extend(ACTIVITY_SUGGESTIONS[activity.lower()])
    
    # Check hobbies
    hobbies = preferences.get("hobbies", [])
    for hobby in hobbies:
        if hobby.lower() in ACTIVITY_SUGGESTIONS:
            suggestions.extend(ACTIVITY_SUGGESTIONS[hobby.lower()])
    
    # Check music preferences
    music_prefs = preferences.get("music_preferences", [])
    if music_prefs:
        suggestions.append(f"Listen to {', '.join(music_prefs[:2])} to improve your mood.")
    
    return suggestions

def get_emotion_insight(emotion: str, recent_entries: List[Dict]) -> str:
    """Generate insight based on emotion patterns"""
    if len(recent_entries) < 2:
        return f"You're currently feeling {emotion}. This is a normal part of emotional well-being."
    
    # Check for patterns
    emotions = [entry.get("analysis", {}).get("emotion", "calm") for entry in recent_entries]
    
    if emotions.count(emotion) >= 3:
        return f"You've been feeling {emotion} frequently lately. Consider exploring what might be contributing to this pattern."
    
    if emotion == "stress":
        return "Stress appears to be a recurring theme. Regular stress management techniques might be helpful."
    elif emotion == "joy":
        return "You've experienced joy recently! Identifying what brings you joy can help cultivate more positive moments."
    else:
        return f"Your recent emotional patterns show variety. This emotional flexibility is a sign of healthy emotional regulation."

def get_general_suggestions(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Get general suggestions when no recent data is available"""
    general_suggestions = [
        "Start a daily journaling practice to track your emotions.",
        "Practice gratitude by listing three things you're thankful for each day.",
        "Take regular breaks throughout the day for mental wellness.",
        "Connect with friends or family members regularly.",
        "Engage in physical activity you enjoy.",
        "Practice mindfulness or meditation for 10 minutes daily."
    ]
    
    preference_suggestions = get_preference_based_suggestions(preferences)
    all_suggestions = general_suggestions + preference_suggestions
    random.shuffle(all_suggestions)
    
    return {
        "suggestions": all_suggestions[:6],
        "based_on": {
            "recent_emotion": "no_data",
            "preferences": list(preferences.keys())
        },
        "insight": "Start by journaling regularly to receive more personalized suggestions based on your emotional patterns."
    }

@router.post("/analyze-mood")
async def analyze_current_mood(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze current mood text and provide immediate suggestions"""
    
    # Analyze the text
    analysis = await ai_analyzer.analyze_text(text, current_user.preferences.dict())
    
    # Get appropriate suggestions
    emotion = analysis.emotion.value
    emotion_suggestions = SUGGESTION_TEMPLATES.get(emotion, [])
    
    # Add preference-based suggestions
    preference_suggestions = get_preference_based_suggestions(current_user.preferences.dict())
    
    all_suggestions = emotion_suggestions + preference_suggestions
    random.shuffle(all_suggestions)
    
    return {
        "analysis": analysis.dict(),
        "suggestions": all_suggestions[:4],
        "quick_tip": get_quick_tip(emotion)
    }

def get_quick_tip(emotion: str) -> str:
    """Get a quick tip for immediate emotional support"""
    quick_tips = {
        "stress": "Take 3 deep breaths. Inhale for 4 counts, hold for 4, exhale for 6.",
        "anxiety": "Ground yourself: Name 5 things you can see, 4 you can touch, 3 you can hear.",
        "sadness": "It's okay to feel sad. Be gentle with yourself and allow the emotion.",
        "anger": "Count to 10 before responding. This gives you time to choose your response.",
        "joy": "Savor this moment! Notice where you feel joy in your body.",
        "fear": "Remind yourself that you are safe right now in this present moment."
    }
    
    return quick_tips.get(emotion, "Take a moment to check in with yourself and your emotions.")

@router.get("/daily-activity")
async def get_daily_activity_suggestion(
    current_user: User = Depends(get_current_user)
):
    """Get a daily activity suggestion based on time and preferences"""
    
    current_hour = datetime.now().hour
    
    # Time-based suggestions
    if 6 <= current_hour < 12:  # Morning
        time_suggestions = [
            "Start your day with 5 minutes of stretching or gentle exercise.",
            "Enjoy a nutritious breakfast while practicing mindful eating.",
            "Set a positive intention for the day ahead.",
            "Take a few moments to plan your priorities for today."
        ]
    elif 12 <= current_hour < 17:  # Afternoon
        time_suggestions = [
            "Take a short break to stretch and move your body.",
            "Step outside for fresh air and natural light.",
            "Practice a brief mindfulness exercise.",
            "Connect with a friend or colleague for a positive interaction."
        ]
    elif 17 <= current_hour < 22:  # Evening
        time_suggestions = [
            "Wind down with a relaxing activity you enjoy.",
            "Reflect on three good things that happened today.",
            "Prepare for a restful evening with calming music or reading.",
            "Connect with loved ones and share about your day."
        ]
    else:  # Night
        time_suggestions = [
            "Practice gentle stretching or yoga before bed.",
            "Try a guided meditation for better sleep.",
            "Write down any worries to set them aside for tomorrow.",
            "Create a peaceful environment for restful sleep."
        ]
    
    # Add preference-based suggestions
    preference_suggestions = get_preference_based_suggestions(current_user.preferences.dict())
    
    all_suggestions = time_suggestions + preference_suggestions
    random.shuffle(all_suggestions)
    
    return {
        "activity_suggestion": all_suggestions[0],
        "time_context": get_time_context(current_hour),
        "encouragement": "Small positive actions throughout the day contribute to overall well-being."
    }

def get_time_context(hour: int) -> str:
    """Get time context for the suggestion"""
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 22:
        return "evening"
    else:
        return "night"
