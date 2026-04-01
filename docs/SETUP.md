# Sereno Platform Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **MongoDB** (running locally or connection string)
- **Git**

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai_mental_healthcompanion
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 4. Start MongoDB

Make sure MongoDB is running on your system:

```bash
# On Windows (if installed as service)
net start MongoDB

# On macOS (using Homebrew)
brew services start mongodb-community

# On Linux
sudo systemctl start mongod
```

### 5. Run the Application

#### Start Backend Server

```bash
# From the backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Development Server

```bash
# From the frontend directory
npm run dev
```

#### Or Run Both Simultaneously

```bash
# From the root directory
npm run dev
```

## Environment Variables

### Backend (.env)

```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
sereno/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry point
│   ├── models/             # Data models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App pages
│   │   ├── components/    # Reusable components
│   │   ├── lib/           # Utilities and API
│   │   └── globals.css   # Global styles
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Tailwind configuration
├── docs/                  # Documentation
└── README.md             # Project overview
```

## Features Overview

### Core Features

1. **User Authentication & Onboarding**
   - User registration and login
   - Personalized preference setup
   - Profile management

2. **AI-Powered Journal Analysis**
   - Text emotion analysis using BERT
   - Sentiment analysis
   - Keyword extraction
   - Personalized insights

3. **Community Support**
   - Community posts and discussions
   - Comments and reactions
   - Media sharing
   - Anonymous participation

4. **Real-time Chat**
   - One-on-one messaging
   - Group discussions
   - Online status indicators

5. **Dashboard & Analytics**
   - Emotion distribution charts
   - Mood trends
   - Well-being score
   - Personalized suggestions

6. **Media Sharing**
   - Image uploads
   - Document sharing
   - File management

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update user profile

### Journal
- `POST /api/journal/entries` - Create journal entry
- `GET /api/journal/entries` - Get journal entries
- `GET /api/journal/entries/{id}` - Get specific entry
- `PUT /api/journal/entries/{id}` - Update entry
- `DELETE /api/journal/entries/{id}` - Delete entry
- `POST /api/journal/analyze` - Analyze text

### Community
- `POST /api/community/posts` - Create post
- `GET /api/community/posts` - Get posts
- `POST /api/community/posts/{id}/reactions` - Add reaction
- `POST /api/community/posts/{id}/comments` - Add comment

### Chat
- `GET /api/chat/conversations` - Get conversations
- `GET /api/chat/messages/{userId}` - Get messages
- `WebSocket /ws/chat/{userId}` - Real-time chat

### Suggestions & Insights
- `GET /api/suggestions/personalized` - Get personalized suggestions
- `GET /api/insights/dashboard` - Get dashboard data
- `GET /api/insights/wellbeing-score` - Get well-being score

## Development Notes

### Code Style

- **Backend**: Follow PEP 8 Python style guidelines
- **Frontend**: Use ESLint and Prettier for consistent formatting
- **Components**: Use TypeScript for type safety

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database

The application uses MongoDB with the following collections:

- `users` - User accounts and preferences
- `journal_entries` - Journal entries and analysis
- `community_posts` - Community posts and comments
- `chat_messages` - Chat messages
- `media_files` - Uploaded media files

## Deployment

### Backend Deployment

1. Set production environment variables
2. Install production dependencies
3. Run with Gunicorn or similar WSGI server
4. Configure reverse proxy (nginx)

### Frontend Deployment

1. Build the application:
   ```bash
   npm run build
   ```
2. Deploy to Vercel, Netlify, or similar platform

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in .env

2. **Port Already in Use**
   - Change port in startup scripts
   - Kill existing processes

3. **CORS Issues**
   - Verify CORS configuration
   - Check frontend API URL

4. **Module Import Errors**
   - Install missing dependencies
   - Check virtual environment activation

### Getting Help

- Check the logs for detailed error messages
- Review API documentation at `/docs`
- Ensure all environment variables are set correctly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
