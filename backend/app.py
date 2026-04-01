from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

app = FastAPI(title="Sereno API", version="1.0.0")

# In-memory storage for testing without MongoDB
users_db = {}
journal_entries_db = {}
community_posts_db = {}
user_id_counter = 1
entry_id_counter = 1
post_id_counter = 1

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sereno API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Simple auth endpoints for testing
@app.post("/api/auth/register")
async def register(user_data: dict):
    global user_id_counter
    user_id = str(user_id_counter)
    user_id_counter += 1
    
    users_db[user_id] = {
        "id": user_id,
        "email": user_data.get("email"),
        "username": user_data.get("username"),
        "full_name": user_data.get("full_name"),
        "preferences": {},
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "anonymous_mode": False
    }
    
    return users_db[user_id]

@app.post("/api/auth/login")
async def login(credentials: dict):
    email = credentials.get("email")
    password = credentials.get("password")
    
    # Find user by email (simplified - no password check for testing)
    for user_id, user in users_db.items():
        if user.get("email") == email:
            return {
                "access_token": "test-token-" + user_id,
                "token_type": "bearer"
            }
    
    return {"detail": "Invalid credentials"}, 401

@app.put("/api/auth/me")
async def update_me(update_data: dict):
    # Update user preferences (simplified)
    user_id = "test-user-1"
    if user_id in users_db:
        users_db[user_id]["preferences"] = update_data.get("preferences", {})
        return users_db[user_id]
    return {"detail": "User not found"}, 404

@app.get("/api/auth/me")
async def get_me():
    # Return a mock user for testing
    return {
        "id": "test-user-1",
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "preferences": {
            "relaxing_activities": ["music", "walking"],
            "hobbies": ["reading", "gaming"],
            "stress_triggers": ["deadlines"],
            "music_preferences": ["classical", "jazz"]
        },
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "anonymous_mode": False
    }

@app.post("/api/journal/entries")
async def create_entry(entry_data: dict):
    global entry_id_counter
    entry_id = str(entry_id_counter)
    entry_id_counter += 1
    
    # Generate AI analysis based on text content and user preferences
    text = entry_data.get("text", "")
    
    # Get user preferences (in real app, this would come from database)
    user_preferences = {
        "relaxing_activities": ["music", "walking", "reading"],
        "hobbies": ["gaming", "sports", "writing"],
        "stress_triggers": ["deadlines", "work pressure"],
        "music_preferences": ["classical", "jazz", "ambient"],
        "preferred_activities": ["indoors", "solo", "creative"],
        "disliked_environments": ["crowded places", "loud noises"],
        "time_of_day_preference": "morning"
    }
    
    # Enhanced emotion detection based on keywords and user preferences
    emotions = {
        "happy": ["happy", "joy", "excited", "wonderful", "amazing", "great", "fantastic", "awesome"],
        "sad": ["sad", "unhappy", "depressed", "down", "disappointed", "blue", "upset", "gloomy"],
        "angry": ["angry", "mad", "furious", "annoyed", "frustrated", "upset", "irritated", "rage"],
        "anxious": ["anxious", "worried", "nervous", "scared", "afraid", "panic", "tense", "fearful"],
        "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "content", "chill", "peace", "zen"],
        "stressed": ["stressed", "overwhelmed", "pressure", "deadline", "work", "busy", "tired", "exhausted"]
    }
    
    detected_emotion = "calm"  # Default
    confidence = 0.5  # Default confidence
    key_words = []
    sentiment_score = 0.0  # Default neutral sentiment
    
    # Detect emotion based on keywords - check all emotions
    text_lower = text.lower()
    emotion_scores = {}  # Track how many keywords match each emotion
    
    for emotion, keywords in emotions.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
                key_words.append(keyword)
        if score > 0:
            emotion_scores[emotion] = score
    
    # Find the emotion with the highest score
    if emotion_scores:
        detected_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = min(0.9, 0.5 + (emotion_scores[detected_emotion] * 0.1))
    
    # Adjust sentiment based on detected emotion
    if detected_emotion in ["happy", "calm", "peaceful", "zen"]:
        sentiment_score = 0.6
    elif detected_emotion in ["sad", "anxious", "stressed", "gloomy", "upset"]:
        sentiment_score = -0.6
    elif detected_emotion in ["angry", "mad", "furious", "irritated", "rage"]:
        sentiment_score = -0.8
    
    # Generate personalized insights and suggestions based on emotion and user preferences
    insights = []
    suggestions = []
    
    if detected_emotion == "stressed":
        if "work" in text_lower:
            insights.append("You're experiencing work-related stress")
            suggestions.append("Consider taking a 5-minute break and practicing deep breathing")
            suggestions.append("Try organizing your tasks to reduce overwhelm")
        else:
            insights.append("You're showing signs of stress")
            suggestions.append("Practice mindfulness meditation for 10 minutes")
            suggestions.append("Try grounding techniques: focus on your senses")
            
        # Add preference-based suggestions
        if "music" in user_preferences.get("relaxing_activities", []):
            suggestions.append("Listen to calming music from your preferred genres")
        if "walking" in user_preferences.get("relaxing_activities", []):
            suggestions.append("Take a short walk to clear your mind")
            
    elif detected_emotion == "happy":
        insights.append("You're in a positive emotional state")
        suggestions.append("Keep up the great work and maintain this positivity")
        suggestions.append("Share your positive energy with others")
        suggestions.append("Consider journaling more to track these good moments")
        
        # Add preference-based suggestions
        if "social" in user_preferences.get("preferred_activities", []):
            suggestions.append("This is a great time to connect with friends")
            
    elif detected_emotion == "anxious":
        insights.append("You're showing signs of anxiety")
        suggestions.append("Practice mindfulness meditation for 10 minutes")
        suggestions.append("Try grounding techniques: focus on your senses")
        suggestions.append("Consider talking to a trusted friend about your feelings")
        
        # Add preference-based suggestions
        if "classical" in user_preferences.get("music_preferences", []):
            suggestions.append("Listen to classical music to help calm your nerves")
        if "reading" in user_preferences.get("hobbies", []):
            suggestions.append("Try reading a calming book to distract your mind")
            
    elif detected_emotion == "calm":
        insights.append("You're in a peaceful, balanced state")
        suggestions.append("This is a great time for reflection and planning")
        suggestions.append("Consider journaling more regularly to maintain this state")
        suggestions.append("Practice gratitude exercises to enhance this peaceful feeling")
        
        # Add preference-based suggestions
        if "creative" in user_preferences.get("preferred_activities", []):
            suggestions.append("Engage in a creative activity like writing or art")
        if "morning" in user_preferences.get("time_of_day_preference", ""):
            suggestions.append("Morning is perfect for peaceful activities like meditation")
            
    else:
        insights.append(f"Your emotional state shows {detected_emotion}")
        suggestions.append("Continue monitoring your emotional patterns")
        
        # Add general preference-based suggestions
        if user_preferences.get("relaxing_activities"):
            suggestions.append(f"Try one of your relaxing activities: {', '.join(user_preferences['relaxing_activities'][:2])}")
    
    analysis = {
        "emotion": detected_emotion,
        "confidence": confidence,
        "key_words": key_words[:5],  # Limit to top 5 keywords
        "sentiment_score": sentiment_score,
        "intensity": "high" if abs(sentiment_score) > 0.7 else "moderate" if abs(sentiment_score) > 0.3 else "low",
        "insights": insights,
        "suggestions": suggestions,
        "personalized": True  # Flag to indicate this uses user preferences
    }
    
    journal_entries_db[entry_id] = {
        "id": entry_id,
        "user_id": "test-user-1",
        "text": entry_data.get("text"),
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "mood_rating": entry_data.get("mood_rating"),
        "tags": entry_data.get("tags", []),
        "is_private": entry_data.get("is_private", True),
        "media_files": []
    }
    
    return journal_entries_db[entry_id]

@app.get("/api/journal/entries")
async def get_entries():
    return list(journal_entries_db.values())

@app.get("/api/suggestions/personalized")
async def get_suggestions():
    return {
        "suggestions": [
            "Take a 5-minute break and practice deep breathing exercises.",
            "Go for a short walk to clear your mind.",
            "Listen to calming music or nature sounds.",
            "Practice mindfulness meditation for 10 minutes.",
            "Write down your thoughts to gain perspective.",
            "Consider talking to a friend about what's bothering you."
        ],
        "based_on": {
            "recent_emotion": "calm",
            "preferences": ["music", "walking"]
        },
        "insight": "You appear to be in a peaceful state."
    }

@app.get("/api/insights/dashboard")
async def get_dashboard():
    # Mock dashboard data
    return {
        "emotion_distribution": {
            "calm": {"count": 15, "percentage": 35.7, "average_confidence": 0.82},
            "joy": {"count": 8, "percentage": 19.0, "average_confidence": 0.91},
            "stress": {"count": 6, "percentage": 14.3, "average_confidence": 0.75}
        },
        "mood_trends": {
            "daily_trends": [
                {"date": "2024-03-27", "average_mood": 6.5, "entry_count": 2},
                {"date": "2024-03-26", "average_mood": 7.2, "entry_count": 1}
            ],
            "trend_direction": "improving",
            "overall_average": 6.8
        },
        "weekly_patterns": {
            "Monday": {"most_common_emotion": "stress", "average_mood": 5.8, "entry_count": 5},
            "Tuesday": {"most_common_emotion": "calm", "average_mood": 7.1, "entry_count": 3}
        },
        "key_insights": [
            "You've been feeling calm frequently lately",
            "Your mood has been improving recently"
        ],
        "summary_stats": {
            "total_entries": 42,
            "entries_this_week": 7,
            "average_mood": 6.8,
            "most_common_emotion": "calm",
            "current_streak": 5
        }
    }

@app.get("/api/community/posts")
async def get_community_posts():
    return list(community_posts_db.values())

@app.post("/api/community/posts")
async def create_community_post(post_data: dict):
    global post_id_counter
    post_id = str(post_id_counter)
    post_id_counter += 1
    
    community_posts_db[post_id] = {
        "id": post_id,
        "user_id": "test-user-1",
        "username": "testuser",
        "anonymous": post_data.get("anonymous", False),
        "title": post_data.get("title"),
        "text": post_data.get("text"),
        "media_files": [],
        "tags": post_data.get("tags", []),
        "timestamp": datetime.now().isoformat(),
        "reactions": {},
        "comments": [],
        "is_edited": False
    }
    
    return community_posts_db[post_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
