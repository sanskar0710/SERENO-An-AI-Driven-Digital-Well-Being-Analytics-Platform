import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from typing import Dict, List, Any
from models import EmotionAnalysis, EmotionCategory

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

class AIAnalyzer:
    def __init__(self):
        # Initialize sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        
        # Initialize emotion classification model
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        
        # Initialize BERT tokenizer for keyword extraction
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        
        # Stop words
        self.stop_words = set(stopwords.words('english'))
        
        # Emotion keywords mapping
        self.emotion_keywords = {
            EmotionCategory.JOY: ['happy', 'joyful', 'excited', 'delighted', 'pleased', 'glad', 'cheerful'],
            EmotionCategory.SADNESS: ['sad', 'unhappy', 'depressed', 'down', 'blue', 'melancholy', 'gloomy'],
            EmotionCategory.ANGER: ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'upset'],
            EmotionCategory.FEAR: ['afraid', 'scared', 'frightened', 'anxious', 'worried', 'nervous', 'terrified'],
            EmotionCategory.SURPRISE: ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered'],
            EmotionCategory.DISGUST: ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated'],
            EmotionCategory.STRESS: ['stressed', 'overwhelmed', 'pressured', 'tense', 'strained', 'burdened'],
            EmotionCategory.ANXIETY: ['anxious', 'worried', 'nervous', 'uneasy', 'apprehensive', 'restless'],
            EmotionCategory.CALM: ['calm', 'relaxed', 'peaceful', 'serene', 'tranquil', 'composed'],
            EmotionCategory.EXCITEMENT: ['excited', 'thrilled', 'enthusiastic', 'eager', 'animated', 'energetic']
        }

    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """Extract important keywords from text"""
        # Clean and tokenize
        cleaned_text = self.clean_text(text)
        tokens = word_tokenize(cleaned_text)
        
        # Remove stop words and short words
        keywords = [word for word in tokens if word not in self.stop_words and len(word) > 2]
        
        # Count word frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]

    def get_sentiment_score(self, text: str) -> float:
        """Get sentiment score using VADER"""
        scores = self.sia.polarity_scores(text)
        return scores['compound']

    def classify_emotion(self, text: str) -> tuple[EmotionCategory, float]:
        """Classify emotion using transformer model"""
        try:
            # Get emotion predictions
            predictions = self.emotion_classifier(text)
            
            # Map model emotions to our categories
            emotion_mapping = {
                'joy': EmotionCategory.JOY,
                'sadness': EmotionCategory.SADNESS,
                'anger': EmotionCategory.ANGER,
                'fear': EmotionCategory.FEAR,
                'surprise': EmotionCategory.SURPRISE,
                'disgust': EmotionCategory.DISGUST,
                'neutral': EmotionCategory.CALM
            }
            
            # Find the emotion with highest score
            best_prediction = max(predictions[0], key=lambda x: x['score'])
            model_emotion = best_prediction['label'].lower()
            confidence = best_prediction['score']
            
            # Map to our emotion category
            emotion = emotion_mapping.get(model_emotion, EmotionCategory.CALM)
            
            # Check for stress/anxiety keywords
            keywords = self.extract_keywords(text)
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['stress', 'overwhelmed', 'pressured']):
                emotion = EmotionCategory.STRESS
            elif any(word in text_lower for word in ['anxious', 'worried', 'nervous']):
                emotion = EmotionCategory.ANXIETY
            elif any(word in text_lower for word in ['excited', 'thrilled', 'enthusiastic']):
                emotion = EmotionCategory.EXCITEMENT
            
            return emotion, confidence
            
        except Exception as e:
            print(f"Error in emotion classification: {e}")
            return EmotionCategory.CALM, 0.5

    def determine_intensity(self, sentiment_score: float, confidence: float) -> str:
        """Determine intensity level based on sentiment and confidence"""
        avg_score = (abs(sentiment_score) + confidence) / 2
        
        if avg_score >= 0.7:
            return "high"
        elif avg_score >= 0.4:
            return "moderate"
        else:
            return "low"

    def generate_insights(self, text: str, emotion: EmotionCategory, user_preferences: Dict[str, Any]) -> List[str]:
        """Generate personalized insights based on emotion and user preferences"""
        insights = []
        
        # Time-based insights
        if "evening" in text.lower() or "night" in text.lower():
            insights.append("You appear to experience different emotions in the evening.")
        
        if "work" in text.lower() or "job" in text.lower():
            insights.append("Work-related experiences seem to influence your emotional state.")
        
        # Preference-based insights
        if emotion == EmotionCategory.STRESS:
            if user_preferences.get('relaxing_activities'):
                activities = user_preferences['relaxing_activities']
                if activities:
                    insights.append(f"You mentioned that {', '.join(activities[:2])} help you relax.")
        
        if emotion == EmotionCategory.JOY:
            if user_preferences.get('hobbies'):
                hobbies = user_preferences['hobbies']
                if hobbies:
                    insights.append(f"Your hobbies like {', '.join(hobbies[:2])} seem to bring you joy.")
        
        return insights

    def generate_suggestions(self, text: str, emotion: EmotionCategory, user_preferences: Dict[str, Any]) -> List[str]:
        """Generate personalized suggestions based on emotion and preferences"""
        suggestions = []
        
        # Emotion-specific suggestions
        if emotion == EmotionCategory.STRESS:
            suggestions.append("Take a few deep breaths and focus on the present moment.")
            
            if user_preferences.get('music_preferences'):
                suggestions.append("Listening to calming music may help reduce stress.")
            
            if 'walking' in user_preferences.get('relaxing_activities', []):
                suggestions.append("A short walk outside might help clear your mind.")
        
        elif emotion == EmotionCategory.SADNESS:
            suggestions.append("It's okay to feel sad. Consider reaching out to a friend.")
            
            if user_preferences.get('hobbies'):
                suggestions.append("Engaging in activities you enjoy might help lift your mood.")
        
        elif emotion == EmotionCategory.ANXIETY:
            suggestions.append("Practice grounding techniques: name 5 things you can see, 4 you can touch, 3 you can hear.")
            suggestions.append("Consider writing down your worries to gain perspective.")
        
        elif emotion == EmotionCategory.JOY:
            suggestions.append("Savor this positive moment and consider what contributed to it.")
            suggestions.append("Sharing your joy with others can amplify the positive feelings.")
        
        # General suggestions
        if "tired" in text.lower() or "exhausted" in text.lower():
            suggestions.append("Consider getting some rest if you're feeling tired.")
        
        return suggestions

    async def analyze_text(self, text: str, user_preferences: Dict[str, Any] = None) -> EmotionAnalysis:
        """Main method to analyze text and return comprehensive analysis"""
        if user_preferences is None:
            user_preferences = {}
        
        # Extract keywords
        keywords = self.extract_keywords(text)
        
        # Get sentiment score
        sentiment_score = self.get_sentiment_score(text)
        
        # Classify emotion
        emotion, confidence = self.classify_emotion(text)
        
        # Determine intensity
        intensity = self.determine_intensity(sentiment_score, confidence)
        
        # Generate insights and suggestions
        insights = self.generate_insights(text, emotion, user_preferences)
        suggestions = self.generate_suggestions(text, emotion, user_preferences)
        
        return EmotionAnalysis(
            emotion=emotion,
            confidence=confidence,
            key_words=keywords,
            sentiment_score=sentiment_score,
            intensity=intensity,
            insights=insights,
            suggestions=suggestions
        )
