# Sereno Platform Architecture

## Overview

Sereno is a full-stack AI-powered digital well-being platform that combines modern web technologies with machine learning to provide personalized mental health support and community engagement.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (MongoDB)     │
│                 │    │                 │    │                 │
│ - React/Next.js │    │ - Python/FastAPI│    │ - User Data     │
│ - Tailwind CSS  │    │ - JWT Auth      │    │ - Journal Entries│
│ - Framer Motion │    │ - ML Models     │    │ - Community     │
│ - Zustand Store │    │ - WebSocket     │    │ - Chat Messages │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI/ML         │    │   File Storage  │    │   External APIs  │
│   Services      │    │                 │    │                 │
│                 │    │ - Media Files   │    │ - Email Service │
│ - BERT Model    │    │ - Documents     │    │ - Analytics     │
│ - NLP Pipeline  │    │ - Images        │    │ - Monitoring    │
│ - Sentiment     │    │                 │    │                 │
│ - Emotion       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS with custom design system
- **Animations**: Framer Motion
- **State Management**: Zustand
- **HTTP Client**: Axios
- **UI Components**: Custom components with Radix UI primitives
- **Charts**: Recharts
- **Notifications**: React Hot Toast
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with bcrypt password hashing
- **ML/AI**: 
  - Transformers (Hugging Face)
  - BERT for emotion classification
  - NLTK for text processing
  - TextBlob for sentiment analysis
- **Real-time**: WebSockets
- **File Handling**: aiofiles
- **Validation**: Pydantic models

### Infrastructure
- **Database**: MongoDB (document-oriented)
- **File Storage**: Local filesystem (configurable for cloud storage)
- **API Documentation**: FastAPI auto-generated Swagger UI
- **Environment Management**: .env files

## Data Flow

### User Authentication Flow
```
1. User submits login/registration form
2. Frontend sends request to FastAPI backend
3. Backend validates credentials with MongoDB
4. Backend generates JWT token
5. Token returned to frontend
6. Token stored in localStorage
7. Subsequent requests include Bearer token
8. Backend validates token on protected routes
```

### Journal Entry Analysis Flow
```
1. User writes journal entry
2. Frontend sends text to backend
3. Backend processes text through AI pipeline:
   - Text cleaning and preprocessing
   - Tokenization using BERT tokenizer
   - Emotion classification using BERT model
   - Sentiment analysis using TextBlob
   - Keyword extraction using NLTK
4. Results stored in MongoDB
5. Analysis returned to frontend
6. Frontend displays insights and suggestions
```

### Real-time Chat Flow
```
1. Client establishes WebSocket connection
2. Connection added to connection manager
3. User sends message via WebSocket
4. Backend validates and stores message
5. Backend forwards message to recipient
6. Both users receive real-time updates
7. Read receipts and typing indicators handled
```

## Database Schema

### Collections

#### Users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  username: String (unique),
  password_hash: String,
  full_name: String,
  preferences: {
    relaxing_activities: [String],
    hobbies: [String],
    stress_triggers: [String],
    music_preferences: [String],
    preferred_activities: [String],
    disliked_environments: [String],
    time_of_day_preference: String
  },
  created_at: Date,
  updated_at: Date,
  is_active: Boolean,
  profile_picture: String,
  bio: String,
  anonymous_mode: Boolean
}
```

#### Journal Entries
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  text: String,
  timestamp: Date,
  analysis: {
    emotion: String,
    confidence: Number,
    key_words: [String],
    sentiment_score: Number,
    intensity: String,
    insights: [String],
    suggestions: [String]
  },
  mood_rating: Number (1-10),
  tags: [String],
  is_private: Boolean,
  media_files: [String]
}
```

#### Community Posts
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  username: String,
  anonymous: Boolean,
  title: String,
  text: String,
  media_files: [String],
  tags: [String],
  timestamp: Date,
  reactions: {
    like: Number,
    love: Number,
    support: Number,
    inspired: Number,
    grateful: Number
  },
  comments: [{
    id: String,
    user_id: ObjectId,
    username: String,
    anonymous: Boolean,
    text: String,
    timestamp: Date,
    reactions: Object,
    is_edited: Boolean,
    edited_at: Date
  }],
  is_edited: Boolean,
  edited_at: Date,
  is_moderated: Boolean,
  moderation_reason: String
}
```

#### Chat Messages
```javascript
{
  _id: ObjectId,
  sender_id: ObjectId,
  receiver_id: ObjectId,
  message: String,
  timestamp: Date,
  is_read: Boolean,
  read_at: Date,
  message_type: String,
  media_url: String,
  reply_to: String
}
```

#### Media Files
```javascript
{
  _id: ObjectId,
  filename: String,
  original_name: String,
  file_path: String,
    file_size: Number,
  mime_type: String,
  uploaded_by: ObjectId,
  upload_date: Date,
  is_public: Boolean
}
```

## AI/ML Pipeline

### Text Analysis Process
```
Input Text
    ↓
Text Cleaning
    ↓
Tokenization (BERT)
    ↓
Emotion Classification (BERT)
    ↓
Sentiment Analysis (TextBlob)
    ↓
Keyword Extraction (NLTK)
    ↓
Personalization Engine
    ↓
Output: Analysis + Suggestions
```

### Emotion Classification Model
- **Model**: j-hartmann/emotion-english-distilroberta-base
- **Emotions**: joy, sadness, anger, fear, surprise, disgust, neutral
- **Additional**: stress, anxiety, calm, excitement (custom mapping)
- **Confidence Threshold**: 0.5 minimum

### Personalization Algorithm
```
1. Analyze current emotion and confidence
2. Check user preferences
3. Review historical patterns
4. Consider time of day
5. Generate contextual suggestions
6. Prioritize based on user behavior
```

## Security Architecture

### Authentication & Authorization
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: RS256 signing with configurable expiration
- **Token Refresh**: Automatic refresh mechanism
- **Role-based Access**: User and admin roles

### Data Protection
- **Input Validation**: Pydantic models on all inputs
- **SQL Injection Prevention**: MongoDB query construction
- **XSS Protection**: Input sanitization and output encoding
- **CORS Configuration**: Restricted origins in production

### Privacy Features
- **Anonymous Mode**: Users can participate anonymously
- **Private Journal Entries**: Optional privacy settings
- **Data Encryption**: Sensitive data encrypted at rest
- **GDPR Compliance**: Data deletion and export capabilities

## Performance Optimization

### Frontend Optimization
- **Code Splitting**: Route-based and component-based splitting
- **Image Optimization**: Next.js Image component
- **Caching**: Service worker for offline functionality
- **Bundle Analysis**: Regular bundle size monitoring

### Backend Optimization
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: MongoDB connection management
- **Caching**: Redis for frequently accessed data
- **Async Processing**: Non-blocking I/O operations

### AI Model Optimization
- **Model Caching**: Pre-loaded models in memory
- **Batch Processing**: Process multiple texts when possible
- **Model Quantization**: Reduced model size for faster inference
- **Fallback Models**: Backup models for high-load scenarios

## Scalability Architecture

### Horizontal Scaling
- **Load Balancer**: nginx or cloud load balancer
- **Multiple Backend Instances**: Stateless FastAPI servers
- **Database Replication**: MongoDB replica sets
- **CDN**: Static assets and media files

### Microservices Potential
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Auth Service  │  │  Journal Service│  │ Community Svc  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌─────────────────┐
                    │  AI/ML Service  │
                    └─────────────────┘
```

## Monitoring & Observability

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging service

### Metrics
- **Application Metrics**: Response times, error rates
- **Business Metrics**: User engagement, sentiment trends
- **Infrastructure Metrics**: CPU, memory, database performance

### Health Checks
- **Application Health**: `/health` endpoint
- **Database Health**: Connection status and response time
- **AI Model Health**: Model availability and performance

## Development Workflow

### Environment Setup
- **Development**: Local Docker Compose setup
- **Staging**: Cloud environment with production-like data
- **Production**: Scalable cloud infrastructure

### CI/CD Pipeline
```
1. Code Commit
2. Automated Tests
3. Build Application
4. Security Scans
5. Deploy to Staging
6. Integration Tests
7. Deploy to Production
8. Monitoring & Rollback
```

### Testing Strategy
- **Unit Tests**: pytest for backend, Jest for frontend
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Playwright for user flows
- **Performance Tests**: Load testing for critical paths

## Future Enhancements

### Advanced AI Features
- **Multi-modal Analysis**: Image and text analysis
- **Predictive Analytics**: Mental health trend prediction
- **Personalized Models**: User-specific fine-tuning
- **Voice Analysis**: Speech emotion recognition

### Platform Expansion
- **Mobile Applications**: React Native apps
- **Wearables Integration**: Health data synchronization
- **Professional Support**: Therapist connection features
- **Group Therapy**: Guided group sessions

### Infrastructure Improvements
- **Edge Computing**: Reduced latency
- **Blockchain**: Data integrity and privacy
- **Advanced Security**: Biometric authentication
- **Compliance**: HIPAA and other regulations

## Architecture Decisions

### Why MongoDB?
- **Flexibility**: Schema-less for evolving data models
- **Scalability**: Horizontal scaling capabilities
- **Performance**: Fast document-based operations
- **JSON Integration**: Native JSON support

### Why FastAPI?
- **Performance**: High-performance async framework
- **Documentation**: Auto-generated API docs
- **Type Safety**: Python type hints integration
- **Modern**: Built-in async/await support

### Why Next.js?
- **SSR/SSG**: SEO optimization and performance
- **Developer Experience**: Excellent DX with hot reload
- **Ecosystem**: Rich React ecosystem
- **Deployment**: Easy deployment to various platforms

This architecture provides a solid foundation for the Sereno platform while maintaining flexibility for future growth and enhancements.
