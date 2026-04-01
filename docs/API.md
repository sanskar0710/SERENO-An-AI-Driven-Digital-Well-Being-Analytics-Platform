# Sereno API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow this format:

```json
{
  "data": {},
  "message": "Success",
  "status": "success"
}
```

Error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "preferences": {},
  "created_at": "2024-01-01T00:00:00Z",
  "is_active": true
}
```

#### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "preferences": {
    "relaxing_activities": ["music", "walking"],
    "hobbies": ["reading", "gaming"],
    "stress_triggers": ["deadlines"],
    "music_preferences": ["classical", "jazz"]
  }
}
```

#### Update User Profile
```http
PUT /api/auth/me
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "preferences": {
    "relaxing_activities": ["music", "meditation"]
  }
}
```

### Journal Entries

#### Create Journal Entry
```http
POST /api/journal/entries
```

**Request Body:**
```json
{
  "text": "I had a stressful day at work today...",
  "mood_rating": 4,
  "tags": ["work", "stress"],
  "is_private": true
}
```

**Response:**
```json
{
  "id": "entry_id",
  "user_id": "user_id",
  "text": "I had a stressful day at work today...",
  "timestamp": "2024-01-01T12:00:00Z",
  "analysis": {
    "emotion": "stress",
    "confidence": 0.85,
    "key_words": ["stressful", "work", "day"],
    "sentiment_score": -0.3,
    "intensity": "moderate",
    "insights": ["You appear to experience higher stress during weekdays"],
    "suggestions": ["Take a short break and practice deep breathing"]
  },
  "mood_rating": 4,
  "tags": ["work", "stress"],
  "is_private": true
}
```

#### Get Journal Entries
```http
GET /api/journal/entries?limit=10&offset=0
```

**Query Parameters:**
- `limit` (optional): Number of entries to return (default: 10)
- `offset` (optional): Number of entries to skip (default: 0)

**Response:**
```json
[
  {
    "id": "entry_id",
    "text": "Journal entry text...",
    "timestamp": "2024-01-01T12:00:00Z",
    "analysis": {
      "emotion": "stress",
      "confidence": 0.85
    },
    "mood_rating": 4,
    "tags": ["work", "stress"]
  }
]
```

#### Get Specific Journal Entry
```http
GET /api/journal/entries/{entry_id}
```

#### Update Journal Entry
```http
PUT /api/journal/entries/{entry_id}
```

**Request Body:**
```json
{
  "text": "Updated journal entry text...",
  "mood_rating": 6,
  "tags": ["work", "stress", "recovery"]
}
```

#### Delete Journal Entry
```http
DELETE /api/journal/entries/{entry_id}
```

#### Analyze Text
```http
POST /api/journal/analyze
```

**Request Body:**
```json
{
  "text": "I'm feeling anxious about the upcoming presentation",
  "user_preferences": {
    "relaxing_activities": ["meditation", "breathing"]
  }
}
```

**Response:**
```json
{
  "emotion": "anxiety",
  "confidence": 0.78,
  "key_words": ["anxious", "upcoming", "presentation"],
  "sentiment_score": -0.2,
  "intensity": "moderate",
  "insights": ["You mentioned meditation helps you relax"],
  "suggestions": ["Practice breathing exercises before the presentation"]
}
```

#### Get Journal Statistics
```http
GET /api/journal/stats
```

**Response:**
```json
{
  "emotion_distribution": [
    {
      "_id": "stress",
      "count": 15
    },
    {
      "_id": "joy",
      "count": 8
    }
  ],
  "mood_trends": [
    {
      "_id": "2024-01-01",
      "avg_mood": 6.5,
      "count": 2
    }
  ],
  "total_entries": 23
}
```

### Community Posts

#### Create Community Post
```http
POST /api/community/posts
```

**Request Body:**
```json
{
  "title": "Finding Peace in Nature",
  "text": "Today I went for a walk in the park and found it incredibly calming...",
  "anonymous": false,
  "tags": ["nature", "peace", "mindfulness"]
}
```

#### Get Community Posts
```http
GET /api/community/posts?limit=20&offset=0&tag=nature
```

**Query Parameters:**
- `limit` (optional): Number of posts to return
- `offset` (optional): Number of posts to skip
- `tag` (optional): Filter by tag

#### Get Specific Post
```http
GET /api/community/posts/{post_id}
```

#### Update Post
```http
PUT /api/community/posts/{post_id}
```

#### Delete Post
```http
DELETE /api/community/posts/{post_id}
```

#### Add Reaction to Post
```http
POST /api/community/posts/{post_id}/reactions
```

**Request Body:**
```json
{
  "reaction_type": "support"
}
```

#### Add Comment to Post
```http
POST /api/community/posts/{post_id}/comments
```

**Request Body:**
```json
{
  "text": "This really resonates with me. Thank you for sharing!",
  "anonymous": false
}
```

#### Update Comment
```http
PUT /api/community/posts/{post_id}/comments/{comment_id}
```

**Request Body:**
```json
{
  "text": "Updated comment text..."
}
```

#### Delete Comment
```http
DELETE /api/community/posts/{post_id}/comments/{comment_id}
```

#### Upload Media to Post
```http
POST /api/community/posts/{post_id}/media
```

**Request:** Multipart form data with files

### Chat

#### Get Conversations
```http
GET /api/chat/conversations
```

**Response:**
```json
[
  {
    "user_id": "other_user_id",
    "username": "jane_doe",
    "full_name": "Jane Doe",
    "profile_picture": "profile_url",
    "last_message": "Hey! How are you doing?",
    "last_timestamp": "2024-01-01T12:00:00Z",
    "unread_count": 2
  }
]
```

#### Get Chat Messages
```http
GET /api/chat/messages/{user_id}?limit=50&offset=0
```

#### Mark Message as Read
```http
POST /api/chat/messages/{message_id}/read
```

#### Get Online Users
```http
GET /api/chat/online-users
```

#### WebSocket Connection
```
ws://localhost:8000/ws/chat/{user_id}
```

**Message Format:**
```json
{
  "type": "chat_message",
  "receiver_id": "other_user_id",
  "message": "Hello!",
  "message_type": "text"
}
```

### Suggestions

#### Get Personalized Suggestions
```http
GET /api/suggestions/personalized
```

**Response:**
```json
{
  "suggestions": [
    "Take a 5-minute break and practice deep breathing exercises.",
    "Go for a short walk to clear your mind.",
    "Listen to calming music or nature sounds."
  ],
  "based_on": {
    "recent_emotion": "stress",
    "preferences": ["music", "walking"]
  },
  "insight": "You appear to experience higher stress during weekdays."
}
```

#### Analyze Current Mood
```http
POST /api/suggestions/analyze-mood
```

**Request Body:**
```json
{
  "text": "I'm feeling overwhelmed with work"
}
```

#### Get Daily Activity Suggestion
```http
GET /api/suggestions/daily-activity
```

### Insights

#### Get Dashboard Data
```http
GET /api/insights/dashboard
```

**Response:**
```json
{
  "emotion_distribution": {
    "stress": {
      "count": 15,
      "percentage": 35.7,
      "average_confidence": 0.82
    },
    "joy": {
      "count": 8,
      "percentage": 19.0,
      "average_confidence": 0.91
    }
  },
  "mood_trends": {
    "daily_trends": [
      {
        "date": "2024-01-01",
        "average_mood": 6.5,
        "entry_count": 2
      }
    ],
    "trend_direction": "improving",
    "overall_average": 6.2
  },
  "weekly_patterns": {
    "Monday": {
      "most_common_emotion": "stress",
      "average_mood": 5.8,
      "entry_count": 5
    }
  },
  "key_insights": [
    "You've been feeling stress frequently lately",
    "Your mood has been improving recently"
  ],
  "summary_stats": {
    "total_entries": 42,
    "entries_this_week": 7,
    "average_mood": 6.2,
    "most_common_emotion": "stress",
    "current_streak": 5
  }
}
```

#### Get Emotion History
```http
GET /api/insights/emotion-history?days=30
```

#### Get Well-being Score
```http
GET /api/insights/wellbeing-score
```

**Response:**
```json
{
  "overall_score": 7.2,
  "components": {
    "emotional_balance": 6.8,
    "mood_stability": 7.5,
    "self_awareness": 8.0,
    "journaling_consistency": 6.5
  },
  "message": "Good wellbeing! Continue your current practices"
}
```

## Error Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 100 requests per minute per user
- 1000 requests per hour per user

## WebSocket Events

### Chat Events

#### New Message
```json
{
  "type": "new_message",
  "message": {
    "id": "message_id",
    "sender_id": "user_id",
    "receiver_id": "other_user_id",
    "message": "Hello!",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "sender_id": "user_id",
  "is_typing": true
}
```

#### Read Receipt
```json
{
  "type": "read_receipt",
  "message_id": "message_id"
}
```

## Data Models

### User
```json
{
  "id": "string",
  "email": "string",
  "username": "string",
  "full_name": "string",
  "preferences": {
    "relaxing_activities": ["string"],
    "hobbies": ["string"],
    "stress_triggers": ["string"],
    "music_preferences": ["string"],
    "preferred_activities": ["string"],
    "disliked_environments": ["string"]
  },
  "created_at": "datetime",
  "is_active": "boolean",
  "anonymous_mode": "boolean"
}
```

### Journal Entry
```json
{
  "id": "string",
  "user_id": "string",
  "text": "string",
  "timestamp": "datetime",
  "analysis": {
    "emotion": "string",
    "confidence": "number",
    "key_words": ["string"],
    "sentiment_score": "number",
    "intensity": "string",
    "insights": ["string"],
    "suggestions": ["string"]
  },
  "mood_rating": "number",
  "tags": ["string"],
  "is_private": "boolean"
}
```

### Community Post
```json
{
  "id": "string",
  "user_id": "string",
  "username": "string",
  "anonymous": "boolean",
  "title": "string",
  "text": "string",
  "media_files": ["string"],
  "tags": ["string"],
  "timestamp": "datetime",
  "reactions": {
    "like": "number",
    "support": "number",
    "love": "number"
  },
  "comments": [
    {
      "id": "string",
      "user_id": "string",
      "username": "string",
      "text": "string",
      "timestamp": "datetime",
      "anonymous": "boolean"
    }
  ]
}
```

## Testing

Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints directly.

## Support

For API support and questions, please refer to the project documentation or create an issue in the repository.
