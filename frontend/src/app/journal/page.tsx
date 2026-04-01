'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Heart, Plus, Calendar, Brain, TrendingUp, Search, Filter } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { journalAPI } from '@/lib/api'
import { formatDate, formatDateTime, getEmotionColor, getEmotionIcon, truncateText } from '@/lib/utils'

interface JournalEntry {
  id: string
  user_id: string
  text: string
  timestamp: string
  analysis?: {
    emotion: string
    confidence: number
    key_words: string[]
    sentiment_score: number
    intensity: string
    insights: string[]
    suggestions: string[]
  }
  mood_rating?: number
  tags: string[]
  is_private: boolean
}

export default function JournalPage() {
  const { user } = useAuthStore()
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedEmotion, setSelectedEmotion] = useState('')
  const [showNewEntry, setShowNewEntry] = useState(false)
  const [newEntry, setNewEntry] = useState({
    text: '',
    mood_rating: 5,
    tags: '',
    is_private: true
  })

  useEffect(() => {
    fetchEntries()
  }, [])

  const fetchEntries = async () => {
    try {
      const response = await journalAPI.getEntries()
      setEntries(response.data)
    } catch (error) {
      console.error('Failed to fetch journal entries:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateEntry = async () => {
    if (!newEntry.text.trim()) return

    try {
      const entryData = {
        text: newEntry.text,
        mood_rating: newEntry.mood_rating,
        tags: newEntry.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        is_private: newEntry.is_private
      }

      const response = await journalAPI.createEntry(entryData)
      setEntries([response.data, ...entries])
      
      // Reset form
      setNewEntry({
        text: '',
        mood_rating: 5,
        tags: '',
        is_private: true
      })
      setShowNewEntry(false)
    } catch (error) {
      console.error('Failed to create entry:', error)
    }
  }

  const filteredEntries = entries.filter(entry => {
    const matchesSearch = entry.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         Array.from(entry.tags).some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesEmotion = !selectedEmotion || entry.analysis?.emotion === selectedEmotion
    return matchesSearch && matchesEmotion
  })

  const uniqueEmotions = [...new Set(entries.map(entry => entry.analysis?.emotion).filter(Boolean))]

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-dots">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      {/* Background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">My Journal</h1>
              <p className="text-gray-600">
                Reflect on your thoughts and track your emotional journey
              </p>
            </div>
            <button
              onClick={() => setShowNewEntry(true)}
              className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>New Entry</span>
            </button>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search entries..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={selectedEmotion}
                onChange={(e) => setSelectedEmotion(e.target.value)}
                className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none"
              >
                <option value="">All Emotions</option>
                {uniqueEmotions.map(emotion => (
                  <option key={emotion} value={emotion}>
                    {getEmotionIcon(emotion)} {emotion}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </motion.div>

        {/* New Entry Modal */}
        {showNewEntry && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50"
            onClick={() => setShowNewEntry(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold mb-6 gradient-text">New Journal Entry</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    How are you feeling today?
                  </label>
                  <textarea
                    value={newEntry.text}
                    onChange={(e) => setNewEntry({ ...newEntry, text: e.target.value })}
                    placeholder="Share your thoughts, feelings, and experiences..."
                    className="w-full h-32 p-4 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-gray-800 bg-white placeholder-gray-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mood Rating: {newEntry.mood_rating}/10
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={newEntry.mood_rating}
                    onChange={(e) => setNewEntry({ ...newEntry, mood_rating: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>1</span>
                    <span>5</span>
                    <span>10</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={newEntry.tags}
                    onChange={(e) => setNewEntry({ ...newEntry, tags: e.target.value })}
                    placeholder="work, stress, happy, family..."
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-800 bg-white placeholder-gray-400"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="private"
                    checked={newEntry.is_private}
                    onChange={(e) => setNewEntry({ ...newEntry, is_private: e.target.checked })}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="private" className="ml-2 text-sm text-gray-700">
                    Keep this entry private
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-4 mt-8">
                <button
                  onClick={() => setShowNewEntry(false)}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateEntry}
                  disabled={!newEntry.text.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  Save Entry
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Journal Entries */}
        <div className="space-y-6">
          {filteredEntries.length > 0 ? (
            filteredEntries.map((entry, index) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg card-hover"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getEmotionIcon(entry.analysis?.emotion)}</span>
                      <div>
                        <p className="font-medium capitalize text-gray-800">
                          {entry.analysis?.emotion || 'Unknown'}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatDateTime(entry.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                  {entry.mood_rating && (
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-5 h-5 text-primary-500" />
                      <span className="font-medium text-gray-700">
                        {entry.mood_rating}/10
                      </span>
                    </div>
                  )}
                </div>

                <div className="mb-4">
                  <p className="text-gray-700 leading-relaxed">
                    {truncateText(entry.text, 300)}
                    {entry.text.length > 300 && (
                      <button className="text-primary-600 hover:text-primary-500 ml-2">
                        Read more
                      </button>
                    )}
                  </p>
                </div>

                {/* Author Information - Only show if it's current user's entry */}
                {entry.user_id === user?.id && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold">
                          {user?.username?.[0]?.toUpperCase() || 'U'}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">
                          {user?.full_name || user?.username || 'Anonymous'}
                        </p>
                        <p className="text-sm text-gray-500">
                          Your journal entry • {formatDateTime(entry.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {entry.analysis?.key_words && entry.analysis.key_words.length > 0 && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      {entry.analysis.key_words.map((word, wordIndex) => (
                        <span
                          key={wordIndex}
                          className="px-3 py-1 bg-gradient-to-r from-primary-100 to-secondary-100 text-primary-700 rounded-full text-sm"
                        >
                          {word}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {entry.tags && entry.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {entry.tags.map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* AI Insights Section */}
                {entry.analysis && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                    <h4 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                      <Brain className="w-5 h-5 mr-2 text-primary-500" />
                      AI Insights
                    </h4>
                    
                    {entry.analysis.insights && entry.analysis.insights.length > 0 && (
                      <div className="mb-3">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Key Insights:</h5>
                        <ul className="space-y-1">
                          {entry.analysis.insights.map((insight, insightIndex) => (
                            <li key={insightIndex} className="text-sm text-gray-600 flex items-start">
                              <span className="w-2 h-2 bg-primary-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                              {insight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {entry.analysis.suggestions && entry.analysis.suggestions.length > 0 && (
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Suggestions:</h5>
                        <ul className="space-y-1">
                          {entry.analysis.suggestions.map((suggestion, suggestionIndex) => (
                            <li key={suggestionIndex} className="text-sm text-gray-600 flex items-start">
                              <span className="w-2 h-2 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                              {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="mt-3 pt-3 border-t border-blue-200">
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Emotion: <span className="font-medium capitalize">{entry.analysis.emotion}</span></span>
                        <span>Confidence: {Math.round((entry.analysis.confidence || 0) * 100)}%</span>
                        <span>Sentiment: {entry.analysis.sentiment_score > 0 ? '😊' : entry.analysis.sentiment_score < 0 ? '😔' : '😐'}</span>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            ))
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="bg-white/80 backdrop-blur-lg rounded-xl p-12 shadow-lg text-center"
            >
              <Heart className="w-16 h-16 mx-auto mb-6 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No journal entries yet</h3>
              <p className="text-gray-600 mb-6">
                Start your journaling journey by writing your first entry
              </p>
              <button
                onClick={() => setShowNewEntry(true)}
                className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover inline-flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>Write First Entry</span>
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
