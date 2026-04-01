from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

from models import User
from main import get_database
from routers.auth import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get comprehensive dashboard insights"""
    
    # Get date ranges
    today = datetime.utcnow()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)
    
    # Get all journal entries for the user
    entries = await db.journal_entries.find({
        "user_id": current_user.id,
        "timestamp": {"$gte": thirty_days_ago}
    }).sort("timestamp", -1).to_list(length=None)
    
    if not entries:
        return get_empty_dashboard()
    
    # Calculate various insights
    emotion_distribution = get_emotion_distribution(entries)
    mood_trends = get_mood_trends(entries)
    weekly_patterns = get_weekly_patterns(entries)
    activity_correlations = get_activity_correlations(entries)
    key_insights = generate_key_insights(entries, current_user.preferences.dict())
    
    return {
        "emotion_distribution": emotion_distribution,
        "mood_trends": mood_trends,
        "weekly_patterns": weekly_patterns,
        "activity_correlations": activity_correlations,
        "key_insights": key_insights,
        "summary_stats": {
            "total_entries": len(entries),
            "entries_this_week": len([e for e in entries if e["timestamp"] >= seven_days_ago]),
            "average_mood": calculate_average_mood(entries),
            "most_common_emotion": get_most_common_emotion(emotion_distribution),
            "current_streak": calculate_current_streak(entries)
        }
    }

def get_emotion_distribution(entries: List[Dict]) -> Dict[str, Any]:
    """Calculate emotion distribution"""
    emotion_counts = defaultdict(int)
    emotion_confidence = defaultdict(list)
    
    for entry in entries:
        analysis = entry.get("analysis", {})
        emotion = analysis.get("emotion", "calm")
        confidence = analysis.get("confidence", 0.5)
        
        emotion_counts[emotion] += 1
        emotion_confidence[emotion].append(confidence)
    
    # Calculate percentages and average confidence
    total_entries = len(entries)
    distribution = {}
    
    for emotion, count in emotion_counts.items():
        avg_confidence = sum(emotion_confidence[emotion]) / len(emotion_confidence[emotion])
        distribution[emotion] = {
            "count": count,
            "percentage": round((count / total_entries) * 100, 1),
            "average_confidence": round(avg_confidence, 2)
        }
    
    return distribution

def get_mood_trends(entries: List[Dict]) -> Dict[str, Any]:
    """Calculate mood trends over time"""
    # Group entries by date
    daily_moods = defaultdict(list)
    
    for entry in entries:
        date = entry["timestamp"].strftime("%Y-%m-%d")
        mood = entry.get("mood_rating")
        if mood:
            daily_moods[date].append(mood)
    
    # Calculate daily averages
    mood_trend = []
    for date in sorted(daily_moods.keys()):
        avg_mood = sum(daily_moods[date]) / len(daily_moods[date])
        mood_trend.append({
            "date": date,
            "average_mood": round(avg_mood, 1),
            "entry_count": len(daily_moods[date])
        })
    
    # Calculate trend direction
    if len(mood_trend) >= 2:
        recent_avg = mood_trend[-1]["average_mood"]
        previous_avg = mood_trend[-2]["average_mood"]
        trend_direction = "improving" if recent_avg > previous_avg else "declining" if recent_avg < previous_avg else "stable"
    else:
        trend_direction = "insufficient_data"
    
    return {
        "daily_trends": mood_trend[-7:],  # Last 7 days
        "trend_direction": trend_direction,
        "overall_average": round(sum(entry.get("mood_rating", 5) for entry in entries) / len(entries), 1)
    }

def get_weekly_patterns(entries: List[Dict]) -> Dict[str, Any]:
    """Analyze weekly patterns"""
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_emotions = defaultdict(lambda: defaultdict(int))
    day_moods = defaultdict(list)
    
    for entry in entries:
        day_of_week = entry["timestamp"].weekday()
        day_name = day_names[day_of_week]
        
        analysis = entry.get("analysis", {})
        emotion = analysis.get("emotion", "calm")
        mood = entry.get("mood_rating")
        
        day_emotions[day_name][emotion] += 1
        if mood:
            day_moods[day_name].append(mood)
    
    # Calculate patterns
    weekly_patterns = {}
    for day_name in day_names:
        emotions = day_emotions[day_name]
        moods = day_moods[day_name]
        
        if emotions:
            most_common = max(emotions.items(), key=lambda x: x[1])
            avg_mood = sum(moods) / len(moods) if moods else 0
            
            weekly_patterns[day_name] = {
                "most_common_emotion": most_common[0],
                "emotion_count": most_common[1],
                "average_mood": round(avg_mood, 1) if moods else None,
                "entry_count": len(moods)
            }
    
    return weekly_patterns

def get_activity_correlations(entries: List[Dict]) -> Dict[str, Any]:
    """Find correlations between activities and emotions"""
    activity_emotions = defaultdict(lambda: defaultdict(list))
    
    for entry in entries:
        text = entry.get("text", "").lower()
        analysis = entry.get("analysis", {})
        emotion = analysis.get("emotion", "calm")
        confidence = analysis.get("confidence", 0.5)
        
        # Look for activity keywords
        activities = ["work", "exercise", "music", "friends", "family", "walking", "reading", "gaming"]
        
        for activity in activities:
            if activity in text:
                activity_emotions[activity][emotion].append(confidence)
    
    # Calculate correlations
    correlations = {}
    for activity, emotions in activity_emotions.items():
        if emotions:
            # Find the most common emotion for this activity
            total_entries = sum(len(confidences) for confidences in emotions.values())
            emotion_percentages = {}
            
            for emotion, confidences in emotions.items():
                percentage = (len(confidences) / total_entries) * 100
                avg_confidence = sum(confidences) / len(confidences)
                emotion_percentages[emotion] = {
                    "percentage": round(percentage, 1),
                    "average_confidence": round(avg_confidence, 2),
                    "count": len(confidences)
                }
            
            correlations[activity] = {
                "total_entries": total_entries,
                "emotion_distribution": emotion_percentages
            }
    
    return correlations

def generate_key_insights(entries: List[Dict], preferences: Dict[str, Any]) -> List[str]:
    """Generate personalized insights"""
    insights = []
    
    if len(entries) < 3:
        insights.append("Continue journaling regularly to receive more personalized insights.")
        return insights
    
    # Analyze emotion patterns
    emotions = [entry.get("analysis", {}).get("emotion", "calm") for entry in entries]
    recent_emotions = emotions[:7]  # Last 7 entries
    
    # Check for recurring emotions
    emotion_counts = defaultdict(int)
    for emotion in recent_emotions:
        emotion_counts[emotion] += 1
    
    most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])
    
    if most_common_emotion[1] >= 4:
        insights.append(f"You've been feeling {most_common_emotion[0]} frequently lately. Consider exploring what might be contributing to this pattern.")
    
    # Check mood trends
    recent_moods = [entry.get("mood_rating") for entry in entries[:7] if entry.get("mood_rating")]
    if len(recent_moods) >= 3:
        avg_recent = sum(recent_moods) / len(recent_moods)
        if avg_recent >= 7:
            insights.append("Your mood has been quite positive recently! Keep up the activities that contribute to your well-being.")
        elif avg_recent <= 4:
            insights.append("You've been experiencing lower moods lately. Consider reaching out for support or trying new coping strategies.")
    
    # Check for time patterns
    entries_by_hour = defaultdict(list)
    for entry in entries:
        hour = entry["timestamp"].hour
        entries_by_hour[hour].append(entry)
    
    # Find most active journaling times
    if entries_by_hour:
        most_active_hour = max(entries_by_hour.items(), key=lambda x: len(x[1]))
        if len(most_active_hour[1]) >= 3:
            insights.append(f"You tend to journal most around {most_active_hour[0]}:00. This might be when you're most reflective.")
    
    # Preference-based insights
    if preferences.get("relaxing_activities"):
        relaxing = preferences["relaxing_activities"]
        if len(relaxing) > 0:
            insights.append(f"You mentioned that {', '.join(relaxing[:2])} help you relax. Consider incorporating these activities more regularly.")
    
    # Check for stress patterns
    stress_entries = [e for e in entries if e.get("analysis", {}).get("emotion") == "stress"]
    if len(stress_entries) >= 3:
        insights.append("Stress appears frequently in your entries. Regular stress management techniques might be beneficial.")
    
    return insights

def calculate_average_mood(entries: List[Dict]) -> float:
    """Calculate average mood rating"""
    moods = [entry.get("mood_rating") for entry in entries if entry.get("mood_rating")]
    return round(sum(moods) / len(moods), 1) if moods else 0

def get_most_common_emotion(distribution: Dict[str, Any]) -> str:
    """Get the most common emotion"""
    if not distribution:
        return "calm"
    
    return max(distribution.items(), key=lambda x: x[1]["count"])[0]

def calculate_current_streak(entries: List[Dict]) -> int:
    """Calculate current journaling streak"""
    if not entries:
        return 0
    
    # Sort entries by date
    sorted_entries = sorted(entries, key=lambda x: x["timestamp"], reverse=True)
    
    streak = 1
    current_date = sorted_entries[0]["timestamp"].date()
    
    for entry in sorted_entries[1:]:
        entry_date = entry["timestamp"].date()
        date_diff = (current_date - entry_date).days
        
        if date_diff == 1:  # Consecutive day
            streak += 1
            current_date = entry_date
        elif date_diff == 0:  # Same day, multiple entries
            continue
        else:  # Break in streak
            break
    
    return streak

def get_empty_dashboard() -> Dict[str, Any]:
    """Return empty dashboard for new users"""
    return {
        "emotion_distribution": {},
        "mood_trends": {
            "daily_trends": [],
            "trend_direction": "no_data",
            "overall_average": 0
        },
        "weekly_patterns": {},
        "activity_correlations": {},
        "key_insights": [
            "Start journaling to receive personalized insights about your emotional patterns.",
            "Regular reflection can help you better understand your emotional well-being.",
            "The more you journal, the more accurate and helpful your insights will become."
        ],
        "summary_stats": {
            "total_entries": 0,
            "entries_this_week": 0,
            "average_mood": 0,
            "most_common_emotion": "no_data",
            "current_streak": 0
        }
    }

@router.get("/emotion-history")
async def get_emotion_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get detailed emotion history"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    entries = await db.journal_entries.find({
        "user_id": current_user.id,
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", 1).to_list(length=None)
    
    emotion_history = []
    for entry in entries:
        analysis = entry.get("analysis", {})
        emotion_history.append({
            "date": entry["timestamp"].isoformat(),
            "emotion": analysis.get("emotion", "calm"),
            "confidence": analysis.get("confidence", 0.5),
            "mood_rating": entry.get("mood_rating"),
            "text_preview": entry.get("text", "")[:100] + "..." if len(entry.get("text", "")) > 100 else entry.get("text", ""),
            "key_words": analysis.get("key_words", [])
        })
    
    return {"emotion_history": emotion_history}

@router.get("/wellbeing-score")
async def get_wellbeing_score(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Calculate overall wellbeing score"""
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    entries = await db.journal_entries.find({
        "user_id": current_user.id,
        "timestamp": {"$gte": thirty_days_ago}
    }).to_list(length=None)
    
    if not entries:
        return {
            "overall_score": 0,
            "components": {
                "emotional_balance": 0,
                "mood_stability": 0,
                "self_awareness": 0,
                "journaling_consistency": 0
            },
            "message": "Start journaling to calculate your wellbeing score."
        }
    
    # Calculate different components
    emotional_balance = calculate_emotional_balance(entries)
    mood_stability = calculate_mood_stability(entries)
    self_awareness = calculate_self_awareness(entries)
    journaling_consistency = calculate_journaling_consistency(entries)
    
    # Calculate overall score
    overall_score = round(
        (emotional_balance + mood_stability + self_awareness + journaling_consistency) / 4, 1
    )
    
    return {
        "overall_score": overall_score,
        "components": {
            "emotional_balance": emotional_balance,
            "mood_stability": mood_stability,
            "self_awareness": self_awareness,
            "journaling_consistency": journaling_consistency
        },
        "message": get_wellbeing_message(overall_score)
    }

def calculate_emotional_balance(entries: List[Dict]) -> float:
    """Calculate emotional balance score"""
    positive_emotions = ["joy", "excitement", "calm"]
    negative_emotions = ["sadness", "anger", "fear", "stress", "anxiety", "disgust"]
    
    positive_count = 0
    negative_count = 0
    
    for entry in entries:
        emotion = entry.get("analysis", {}).get("emotion", "calm")
        if emotion in positive_emotions:
            positive_count += 1
        elif emotion in negative_emotions:
            negative_count += 1
    
    total_emotional_entries = positive_count + negative_count
    if total_emotional_entries == 0:
        return 5.0  # Neutral score
    
    balance_ratio = positive_count / total_emotional_entries
    return round(balance_ratio * 10, 1)

def calculate_mood_stability(entries: List[Dict]) -> float:
    """Calculate mood stability score"""
    moods = [entry.get("mood_rating") for entry in entries if entry.get("mood_rating")]
    
    if len(moods) < 2:
        return 5.0
    
    # Calculate standard deviation
    avg_mood = sum(moods) / len(moods)
    variance = sum((mood - avg_mood) ** 2 for mood in moods) / len(moods)
    std_dev = variance ** 0.5
    
    # Lower standard deviation = higher stability
    stability_score = max(0, 10 - (std_dev * 2))
    return round(stability_score, 1)

def calculate_self_awareness(entries: List[Dict]) -> float:
    """Calculate self-awareness score based on journaling depth"""
    awareness_score = 0
    
    for entry in entries:
        text = entry.get("text", "")
        analysis = entry.get("analysis", {})
        
        # Longer entries suggest deeper reflection
        if len(text) > 100:
            awareness_score += 1
        
        # Entries with mood ratings show self-awareness
        if entry.get("mood_rating"):
            awareness_score += 1
        
        # Entries with multiple emotions show nuance
        if analysis.get("key_words"):
            awareness_score += len(analysis["key_words"]) * 0.5
    
    max_possible_score = len(entries) * 3
    if max_possible_score == 0:
        return 5.0
    
    normalized_score = (awareness_score / max_possible_score) * 10
    return round(min(normalized_score, 10), 1)

def calculate_journaling_consistency(entries: List[Dict]) -> float:
    """Calculate journaling consistency score"""
    if not entries:
        return 0.0
    
    # Count unique days
    unique_days = set()
    for entry in entries:
        unique_days.add(entry["timestamp"].date())
    
    # Calculate consistency over the last 30 days
    days_in_period = 30
    consistency_ratio = len(unique_days) / days_in_period
    
    return round(consistency_ratio * 10, 1)

def get_wellbeing_message(score: float) -> str:
    """Get appropriate message based on wellbeing score"""
    if score >= 8:
        return "Excellent wellbeing! You're showing strong emotional health and self-awareness."
    elif score >= 6:
        return "Good wellbeing! Continue your current practices and consider areas for improvement."
    elif score >= 4:
        return "Moderate wellbeing. Focus on consistency and explore new coping strategies."
    else:
        return "Your wellbeing could use some attention. Consider reaching out for support and focusing on self-care."
