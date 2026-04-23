from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
from typing import Optional, List
import hashlib
import uuid
import json
import os
import random

# JWT handling
try:
    from jose import jwt, JWTError
except ImportError:
    # Fallback: simple base64 token
    jwt = None
    JWTError = Exception

app = FastAPI(title="Sereno API", version="1.0.0")

# ── Config ──
SECRET_KEY = os.getenv("SECRET_KEY", "sereno-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# ── In-memory storage ──
users_db = {}
journal_entries_db = {}
community_posts_db = {}

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helpers ──
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(email: str) -> str:
    if jwt:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return f"token-{hashlib.md5(email.encode()).hexdigest()}"

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        return "seed-user-1"
    token = authorization.replace("Bearer ", "")
    if jwt:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            for uid, u in users_db.items():
                if u["email"] == email:
                    return uid
        except JWTError:
            pass
    else:
        for uid, u in users_db.items():
            if f"token-{hashlib.md5(u['email'].encode()).hexdigest()}" == token:
                return uid
    return "seed-user-1"

# ── AI Text Analysis ──
EMOTIONS = {
    "happy": ["happy", "joy", "excited", "wonderful", "amazing", "great", "fantastic", "awesome", "love", "loved", "glad", "cheerful", "delighted", "pleased", "thrilled"],
    "sad": ["sad", "unhappy", "depressed", "down", "disappointed", "blue", "upset", "gloomy", "lonely", "heartbroken", "miserable", "hopeless"],
    "angry": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated", "rage", "hate", "disgusted"],
    "anxious": ["anxious", "worried", "nervous", "scared", "afraid", "panic", "tense", "fearful", "uneasy", "dread"],
    "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "content", "chill", "peace", "zen", "mindful", "grateful", "thankful"],
    "stressed": ["stressed", "overwhelmed", "pressure", "deadline", "busy", "tired", "exhausted", "burnout", "overworked", "drained"],
}

SUGGESTIONS_MAP = {
    "happy": [
        "Keep up the great energy! Consider journaling more to track these positive moments.",
        "Share your positivity with someone who might need it today.",
        "This is a great time to set new goals while you're feeling motivated.",
    ],
    "sad": [
        "It's okay to feel sad. Be gentle with yourself today.",
        "Reach out to a friend or family member — connection can help.",
        "Try a comforting activity like watching your favorite show or listening to music.",
        "Consider a short walk outside — fresh air can shift your perspective.",
    ],
    "angry": [
        "Take 3 deep breaths. Inhale for 4 counts, hold for 4, exhale for 6.",
        "Remove yourself from the situation temporarily if possible.",
        "Physical activity can help release built-up tension.",
        "Try writing down what's bothering you to gain clarity.",
    ],
    "anxious": [
        "Try the 5-4-3-2-1 grounding technique: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
        "Practice box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s.",
        "Remind yourself that this feeling is temporary and will pass.",
        "Consider talking to someone you trust about what's worrying you.",
    ],
    "calm": [
        "Wonderful! This peaceful state is great for reflection and planning.",
        "Consider journaling regularly to maintain this emotional balance.",
        "Practice gratitude exercises to enhance this peaceful feeling.",
        "This is a perfect time for creative activities or learning something new.",
    ],
    "stressed": [
        "Take a 5-minute break and practice deep breathing.",
        "Try organizing your tasks — breaking things into smaller steps helps.",
        "Listen to calming music or nature sounds.",
        "Consider a short walk to clear your mind.",
        "Remember: you don't have to do everything at once.",
    ],
}

def analyze_text(text: str, user_prefs: dict = None):
    text_lower = text.lower()
    scores = {}
    key_words = []
    for emotion, keywords in EMOTIONS.items():
        score = 0
        for kw in keywords:
            if kw in text_lower:
                score += 1
                if kw not in key_words:
                    key_words.append(kw)
        if score > 0:
            scores[emotion] = score

    detected = max(scores, key=scores.get) if scores else "calm"
    confidence = min(0.95, 0.5 + (scores.get(detected, 0) * 0.12))

    sentiment = 0.0
    if detected in ["happy", "calm"]:
        sentiment = 0.6 + random.uniform(0, 0.3)
    elif detected in ["sad", "anxious", "stressed"]:
        sentiment = -(0.4 + random.uniform(0, 0.4))
    elif detected == "angry":
        sentiment = -(0.6 + random.uniform(0, 0.3))

    insights = []
    if detected == "stressed" and ("work" in text_lower or "deadline" in text_lower):
        insights.append("Work-related stress detected. Consider setting boundaries.")
    elif detected == "stressed":
        insights.append("You're showing signs of stress. Regular breaks can help.")
    elif detected == "happy":
        insights.append("You're in a positive emotional state — great!")
    elif detected == "sad":
        insights.append("You're experiencing sadness. Remember, it's okay to not be okay.")
    elif detected == "anxious":
        insights.append("Anxiety patterns detected. Grounding techniques may help.")
    elif detected == "calm":
        insights.append("You're in a peaceful, balanced state.")
    else:
        insights.append(f"Your emotional state shows {detected}.")

    suggestions = SUGGESTIONS_MAP.get(detected, SUGGESTIONS_MAP["calm"])[:3]

    if user_prefs:
        if "music" in str(user_prefs.get("relaxing_activities", [])).lower():
            suggestions.append("Listening to calming music from your preferred genres might help.")
        if "walking" in str(user_prefs.get("relaxing_activities", [])).lower():
            suggestions.append("A short walk could do wonders for your mood right now.")

    return {
        "emotion": detected,
        "confidence": round(confidence, 2),
        "key_words": key_words[:5],
        "sentiment_score": round(sentiment, 2),
        "intensity": "high" if abs(sentiment) > 0.7 else "moderate" if abs(sentiment) > 0.3 else "low",
        "insights": insights,
        "suggestions": suggestions,
        "personalized": bool(user_prefs),
    }

# ── Seed Data ──
def create_seed_data():
    uid = "seed-user-1"
    users_db[uid] = {
        "id": uid, "email": "demo@sereno.com", "username": "demo_user",
        "password_hash": hash_password("demo123"), "full_name": "Demo User",
        "preferences": {
            "relaxing_activities": ["Music", "Walking", "Reading"],
            "hobbies": ["Gaming", "Writing", "Photography"],
            "stress_triggers": ["Deadlines", "Work Pressure"],
            "music_preferences": ["Classical", "Lo-fi", "Ambient"],
            "preferred_activities": ["Indoors", "Creative", "Solo"],
            "disliked_environments": ["Crowded places", "Loud noises"],
            "time_of_day_preference": "Morning",
        },
        "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "is_active": True, "anonymous_mode": False, "bio": "Wellness enthusiast 🌿",
    }

    entries_data = [
        ("I had a wonderful day at the park with friends. Feeling so happy and grateful!", 8, ["gratitude", "social"], -5),
        ("Work deadlines are piling up and I feel overwhelmed and stressed.", 4, ["work", "stress"], -3),
        ("Feeling calm and peaceful after my morning meditation session.", 9, ["meditation", "mindfulness"], -2),
        ("I'm worried about the upcoming presentation. Feeling quite anxious.", 3, ["work", "anxiety"], -1),
        ("Had an amazing workout today! Feeling excited and energized.", 8, ["exercise", "health"], -0.5),
        ("The weekend was relaxing. Spent time reading and listening to music.", 7, ["weekend", "relaxation"], -4),
        ("Feeling a bit down today. Nothing seems to be going right.", 3, ["sad", "reflection"], -6),
    ]

    for i, (text, mood, tags, days_offset) in enumerate(entries_data):
        eid = f"seed-entry-{i+1}"
        ts = datetime.now() + timedelta(days=days_offset)
        analysis = analyze_text(text, users_db[uid]["preferences"])
        journal_entries_db[eid] = {
            "id": eid, "user_id": uid, "text": text,
            "timestamp": ts.isoformat(), "analysis": analysis,
            "mood_rating": mood, "tags": tags, "is_private": True, "media_files": [],
        }

    posts_data = [
        ("Finding Peace in Small Moments", "Today I realized that happiness isn't about big achievements. It's in the small moments — a warm cup of tea, a smile from a stranger.", ["mindfulness", "gratitude", "peace"], False),
        ("My Journey with Meditation", "Started meditating 3 months ago and it has completely changed my perspective. Anyone else experienced this?", ["meditation", "wellness", "journey"], False),
        ("Support Needed", "Going through a tough time. Just wanted to share and feel heard. Thanks for being such a supportive community.", ["support", "community", "healing"], True),
        ("Gratitude Practice", "Day 30 of my gratitude journal! Three things I'm grateful for today: 1) Good health 2) Supportive friends 3) Beautiful weather", ["gratitude", "challenge", "positivity"], False),
    ]

    for i, (title, text, tags, anon) in enumerate(posts_data):
        pid = f"seed-post-{i+1}"
        community_posts_db[pid] = {
            "id": pid, "user_id": uid, "username": "Anonymous" if anon else "demo_user",
            "anonymous": anon, "title": title, "text": text, "media_files": [],
            "tags": tags, "timestamp": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "reactions": {"like": random.randint(3, 15), "support": random.randint(1, 8), "love": random.randint(0, 5)},
            "comments": [
                {"id": f"comment-{pid}-1", "user_id": "seed-user-2", "username": "wellness_friend",
                 "anonymous": False, "text": "Thank you for sharing! 💛",
                 "timestamp": (datetime.now() - timedelta(days=i*2-1)).isoformat(),
                 "reactions": {}, "is_edited": False}
            ],
            "is_edited": False,
        }

create_seed_data()

# ══════════════════════════════════════
# ── ROUTES ──
# ══════════════════════════════════════

@app.get("/")
async def root():
    return {"message": "Sereno API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ── AUTH ──
@app.post("/api/auth/register")
async def register(user_data: dict):
    email = user_data.get("email", "")
    for u in users_db.values():
        if u["email"] == email:
            raise HTTPException(400, "Email already registered")

    uid = str(uuid.uuid4())
    users_db[uid] = {
        "id": uid, "email": email, "username": user_data.get("username", ""),
        "password_hash": hash_password(user_data.get("password", "")),
        "full_name": user_data.get("full_name", ""),
        "preferences": {}, "created_at": datetime.now().isoformat(),
        "is_active": True, "anonymous_mode": False, "bio": "",
    }
    return {k: v for k, v in users_db[uid].items() if k != "password_hash"}

@app.post("/api/auth/login")
async def login(credentials: dict):
    email = credentials.get("email", "")
    pw_hash = hash_password(credentials.get("password", ""))
    for u in users_db.values():
        if u["email"] == email and u["password_hash"] == pw_hash:
            return {"access_token": create_token(email), "token_type": "bearer"}
    raise HTTPException(401, "Invalid email or password")

@app.get("/api/auth/me")
async def get_me(authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    user = users_db.get(uid)
    if not user:
        raise HTTPException(404, "User not found")
    return {k: v for k, v in user.items() if k != "password_hash"}

@app.put("/api/auth/me")
async def update_me(update_data: dict, authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    if uid not in users_db:
        raise HTTPException(404, "User not found")
    if "preferences" in update_data:
        existing = users_db[uid].get("preferences", {})
        existing.update(update_data["preferences"])
        users_db[uid]["preferences"] = existing
    if "full_name" in update_data:
        users_db[uid]["full_name"] = update_data["full_name"]
    if "bio" in update_data:
        users_db[uid]["bio"] = update_data["bio"]
    if "anonymous_mode" in update_data:
        users_db[uid]["anonymous_mode"] = update_data["anonymous_mode"]
    return {k: v for k, v in users_db[uid].items() if k != "password_hash"}

# ── JOURNAL ──
@app.post("/api/journal/entries")
async def create_entry(entry_data: dict, authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    user = users_db.get(uid, {})
    text = entry_data.get("text", "")
    analysis = analyze_text(text, user.get("preferences", {}))

    eid = str(uuid.uuid4())
    journal_entries_db[eid] = {
        "id": eid, "user_id": uid, "text": text,
        "timestamp": datetime.now().isoformat(), "analysis": analysis,
        "mood_rating": entry_data.get("mood_rating"),
        "tags": entry_data.get("tags", []), "is_private": entry_data.get("is_private", True),
        "media_files": [],
    }
    return journal_entries_db[eid]

@app.get("/api/journal/entries")
async def get_entries(authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    entries = [e for e in journal_entries_db.values() if e["user_id"] == uid]
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    return entries

# ── SUGGESTIONS ──
@app.get("/api/suggestions/personalized")
async def get_suggestions(authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    user = users_db.get(uid, {})
    prefs = user.get("preferences", {})
    entries = [e for e in journal_entries_db.values() if e["user_id"] == uid]
    entries.sort(key=lambda x: x["timestamp"], reverse=True)

    emotion = entries[0]["analysis"]["emotion"] if entries else "calm"
    base = SUGGESTIONS_MAP.get(emotion, SUGGESTIONS_MAP["calm"])[:]
    if prefs.get("relaxing_activities"):
        for act in prefs["relaxing_activities"][:2]:
            base.append(f"Try {act.lower()} — it's one of your preferred relaxing activities.")
    random.shuffle(base)
    return {
        "suggestions": base[:6],
        "based_on": {"recent_emotion": emotion, "preferences": list(prefs.keys())},
        "insight": f"Based on your recent entries, you've been feeling {emotion}.",
    }

@app.get("/api/suggestions/daily-activity")
async def get_daily_activity(authorization: Optional[str] = Header(None)):
    hour = datetime.now().hour
    if 6 <= hour < 12:
        tip = "Start your day with 5 minutes of stretching or meditation."
    elif 12 <= hour < 17:
        tip = "Take a short break — step outside for fresh air."
    elif 17 <= hour < 22:
        tip = "Wind down with a relaxing activity you enjoy."
    else:
        tip = "Practice gentle stretching or a guided sleep meditation."
    return {"activity_suggestion": tip, "time_context": "morning" if hour < 12 else "afternoon" if hour < 17 else "evening" if hour < 22 else "night", "encouragement": "Small positive actions contribute to overall well-being."}

@app.post("/api/suggestions/analyze-mood")
async def analyze_mood(data: dict, authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    user = users_db.get(uid, {})
    text = data.get("text", "")
    analysis = analyze_text(text, user.get("preferences", {}))
    return {"analysis": analysis, "suggestions": analysis["suggestions"][:4], "quick_tip": "Take a moment to breathe and be present."}

# ── INSIGHTS ──
@app.get("/api/insights/dashboard")
async def get_dashboard(authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    entries = [e for e in journal_entries_db.values() if e["user_id"] == uid]
    entries.sort(key=lambda x: x["timestamp"], reverse=True)

    if not entries:
        return {"emotion_distribution": {}, "mood_trends": {"daily_trends": [], "trend_direction": "no_data", "overall_average": 0}, "weekly_patterns": {}, "key_insights": ["Start journaling to receive personalized insights."], "summary_stats": {"total_entries": 0, "entries_this_week": 0, "average_mood": 0, "most_common_emotion": "no_data", "current_streak": 0}}

    # Emotion distribution
    emo_counts = {}
    for e in entries:
        emo = e.get("analysis", {}).get("emotion", "calm")
        emo_counts[emo] = emo_counts.get(emo, 0) + 1
    total = len(entries)
    emo_dist = {}
    for emo, cnt in emo_counts.items():
        emo_dist[emo] = {"count": cnt, "percentage": round(cnt / total * 100, 1), "average_confidence": 0.82}

    # Mood trends
    moods = [e.get("mood_rating") for e in entries if e.get("mood_rating")]
    avg_mood = round(sum(moods) / len(moods), 1) if moods else 0

    # Daily trends
    daily = {}
    for e in entries:
        d = e["timestamp"][:10]
        if d not in daily:
            daily[d] = []
        if e.get("mood_rating"):
            daily[d].append(e["mood_rating"])
    daily_trends = [{"date": d, "average_mood": round(sum(m)/len(m), 1), "entry_count": len(m)} for d, m in sorted(daily.items()) if m]

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    this_week = [e for e in entries if e["timestamp"] >= week_ago]
    most_common = max(emo_counts, key=emo_counts.get) if emo_counts else "calm"

    insights = [f"You've been feeling {most_common} frequently lately.", f"Your average mood is {avg_mood}/10 — {'great' if avg_mood >= 7 else 'keep going' if avg_mood >= 5 else 'consider trying new coping strategies'}."]
    if len(entries) >= 5:
        insights.append("Great consistency! Regular journaling improves emotional awareness.")

    return {
        "emotion_distribution": emo_dist,
        "mood_trends": {"daily_trends": daily_trends[-7:], "trend_direction": "improving" if len(daily_trends) >= 2 and daily_trends[-1]["average_mood"] >= daily_trends[-2]["average_mood"] else "stable", "overall_average": avg_mood},
        "weekly_patterns": {},
        "key_insights": insights,
        "summary_stats": {"total_entries": total, "entries_this_week": len(this_week), "average_mood": avg_mood, "most_common_emotion": most_common, "current_streak": min(len(entries), 7)},
    }

@app.get("/api/insights/emotion-history")
async def get_emotion_history(days: int = 30, authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    entries = [e for e in journal_entries_db.values() if e["user_id"] == uid]
    entries.sort(key=lambda x: x["timestamp"])
    return {"emotion_history": [{"date": e["timestamp"], "emotion": e.get("analysis", {}).get("emotion", "calm"), "confidence": e.get("analysis", {}).get("confidence", 0.5), "mood_rating": e.get("mood_rating"), "text_preview": e["text"][:100]} for e in entries]}

@app.get("/api/insights/wellbeing-score")
async def get_wellbeing_score(authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    entries = [e for e in journal_entries_db.values() if e["user_id"] == uid]
    if not entries:
        return {"overall_score": 0, "components": {"emotional_balance": 0, "mood_stability": 0, "self_awareness": 0, "journaling_consistency": 0}, "message": "Start journaling to calculate your wellbeing score."}
    pos = sum(1 for e in entries if e.get("analysis", {}).get("emotion") in ["happy", "calm"])
    score = round((pos / len(entries)) * 10, 1) if entries else 5
    return {"overall_score": score, "components": {"emotional_balance": score, "mood_stability": 7.2, "self_awareness": 6.8, "journaling_consistency": min(10, len(entries))}, "message": "Good wellbeing! Continue your current practices."}

# ── COMMUNITY ──
@app.get("/api/community/posts")
async def get_community_posts():
    posts = list(community_posts_db.values())
    posts.sort(key=lambda x: x["timestamp"], reverse=True)
    return posts

@app.post("/api/community/posts")
async def create_community_post(post_data: dict, authorization: Optional[str] = Header(None)):
    uid = get_current_user_id(authorization)
    user = users_db.get(uid, {})
    pid = str(uuid.uuid4())
    community_posts_db[pid] = {
        "id": pid, "user_id": uid,
        "username": "Anonymous" if post_data.get("anonymous") else user.get("username", "user"),
        "anonymous": post_data.get("anonymous", False), "title": post_data.get("title", ""),
        "text": post_data.get("text", ""), "media_files": [], "tags": post_data.get("tags", []),
        "timestamp": datetime.now().isoformat(), "reactions": {"like": 0, "support": 0, "love": 0},
        "comments": [], "is_edited": False,
    }
    return community_posts_db[pid]

@app.post("/api/community/posts/{post_id}/reactions")
async def add_reaction(post_id: str, reaction: dict):
    if post_id not in community_posts_db:
        raise HTTPException(404, "Post not found")
    rt = reaction.get("reaction_type", "like")
    community_posts_db[post_id]["reactions"][rt] = community_posts_db[post_id]["reactions"].get(rt, 0) + 1
    return {"message": "Reaction added"}

@app.post("/api/community/posts/{post_id}/comments")
async def add_comment(post_id: str, comment: dict, authorization: Optional[str] = Header(None)):
    if post_id not in community_posts_db:
        raise HTTPException(404, "Post not found")
    uid = get_current_user_id(authorization)
    user = users_db.get(uid, {})
    c = {"id": str(uuid.uuid4()), "user_id": uid, "username": user.get("username", "user"), "anonymous": comment.get("anonymous", False), "text": comment.get("text", ""), "timestamp": datetime.now().isoformat(), "reactions": {}, "is_edited": False}
    community_posts_db[post_id]["comments"].append(c)
    return c

# ── CHAT ──
@app.get("/api/chat/conversations")
async def get_conversations(authorization: Optional[str] = Header(None)):
    return [
        {"user_id": "user-alice", "username": "Alice", "full_name": "Alice Johnson", "profile_picture": None, "last_message": "Hey! How are you doing today?", "last_timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "unread_count": 2},
        {"user_id": "user-bob", "username": "Bob", "full_name": "Bob Smith", "profile_picture": None, "last_message": "Thanks for the support! Really appreciate it.", "last_timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "unread_count": 0},
        {"user_id": "sereno-ai", "username": "Sereno AI", "full_name": "AI Wellness Assistant", "profile_picture": None, "last_message": "Welcome to Sereno! How can I help you today?", "last_timestamp": (datetime.now() - timedelta(days=1)).isoformat(), "unread_count": 1},
    ]

@app.get("/api/chat/messages/{user_id}")
async def get_chat_messages(user_id: str):
    now = datetime.now()
    if user_id == "sereno-ai":
        return [
            {"id": "m1", "sender_id": "sereno-ai", "receiver_id": "seed-user-1", "message": "Welcome to Sereno! 🌿 I'm here to support your wellness journey.", "timestamp": (now - timedelta(hours=24)).isoformat(), "is_read": True},
            {"id": "m2", "sender_id": "sereno-ai", "receiver_id": "seed-user-1", "message": "How are you feeling today? Feel free to share your thoughts.", "timestamp": (now - timedelta(hours=23)).isoformat(), "is_read": True},
        ]
    elif user_id == "user-alice":
        return [
            {"id": "m3", "sender_id": "user-alice", "receiver_id": "seed-user-1", "message": "Hey! How are you doing today?", "timestamp": (now - timedelta(hours=2)).isoformat(), "is_read": True},
            {"id": "m4", "sender_id": "seed-user-1", "receiver_id": "user-alice", "message": "I'm doing well, thanks! Had a great meditation session this morning.", "timestamp": (now - timedelta(hours=1, minutes=45)).isoformat(), "is_read": True},
            {"id": "m5", "sender_id": "user-alice", "receiver_id": "seed-user-1", "message": "That's awesome! I've been wanting to start meditating too.", "timestamp": (now - timedelta(hours=1)).isoformat(), "is_read": False},
        ]
    return [
        {"id": "m6", "sender_id": user_id, "receiver_id": "seed-user-1", "message": "Thanks for the support! Really appreciate it.", "timestamp": (now - timedelta(hours=3)).isoformat(), "is_read": True},
    ]

@app.get("/api/chat/online-users")
async def get_online_users():
    return {"online_users": ["user-alice", "sereno-ai"]}

@app.post("/api/chat/messages/{message_id}/read")
async def mark_read(message_id: str):
    return {"message": "Message marked as read"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
