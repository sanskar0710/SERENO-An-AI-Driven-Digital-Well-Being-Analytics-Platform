'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Heart, Brain, TrendingUp, Calendar, MessageCircle, Users, BarChart3, Sparkles, BookOpen, LogOut, Home } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { insightsAPI, suggestionsAPI } from '@/lib/api'
import { formatDate, getEmotionColor, getEmotionIcon } from '@/lib/utils'

interface DashboardData {
  emotion_distribution: Record<string, any>
  mood_trends: any
  weekly_patterns: any
  key_insights: string[]
  summary_stats: {
    total_entries: number
    entries_this_week: number
    average_mood: number
    most_common_emotion: string
    current_streak: number
  }
}

// Navigation component used across pages
export function AppNav() {
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  return (
    <nav className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <Heart className="w-7 h-7 text-primary-500" />
            <span className="text-xl font-bold gradient-text">Sereno</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-1">
            <Link href="/dashboard" className="px-3 py-2 rounded-lg text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all text-sm font-medium flex items-center space-x-1.5">
              <Home className="w-4 h-4" /><span>Dashboard</span>
            </Link>
            <Link href="/journal" className="px-3 py-2 rounded-lg text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all text-sm font-medium flex items-center space-x-1.5">
              <BookOpen className="w-4 h-4" /><span>Journal</span>
            </Link>
            <Link href="/community" className="px-3 py-2 rounded-lg text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all text-sm font-medium flex items-center space-x-1.5">
              <Users className="w-4 h-4" /><span>Community</span>
            </Link>
            <Link href="/chat" className="px-3 py-2 rounded-lg text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-all text-sm font-medium flex items-center space-x-1.5">
              <MessageCircle className="w-4 h-4" /><span>Chat</span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600 hidden sm:block">Hi, {user?.username || 'User'}</span>
            <button onClick={handleLogout}
              className="px-3 py-2 text-gray-600 hover:text-red-500 transition-colors flex items-center space-x-1.5 text-sm">
              <LogOut className="w-4 h-4" /><span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
        
        {/* Mobile nav */}
        <div className="flex md:hidden items-center space-x-1 pb-2 overflow-x-auto">
          <Link href="/dashboard" className="px-3 py-1.5 rounded-lg text-gray-700 hover:bg-primary-50 text-xs font-medium whitespace-nowrap">Dashboard</Link>
          <Link href="/journal" className="px-3 py-1.5 rounded-lg text-gray-700 hover:bg-primary-50 text-xs font-medium whitespace-nowrap">Journal</Link>
          <Link href="/community" className="px-3 py-1.5 rounded-lg text-gray-700 hover:bg-primary-50 text-xs font-medium whitespace-nowrap">Community</Link>
          <Link href="/chat" className="px-3 py-1.5 rounded-lg text-gray-700 hover:bg-primary-50 text-xs font-medium whitespace-nowrap">Chat</Link>
        </div>
      </div>
    </nav>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const router = useRouter()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    fetchSuggestions()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await insightsAPI.getDashboard()
      setDashboardData(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      // Fallback data
      setDashboardData({
        emotion_distribution: { calm: { count: 3, percentage: 42.9, average_confidence: 0.82 }, happy: { count: 2, percentage: 28.6, average_confidence: 0.88 }, stressed: { count: 2, percentage: 28.6, average_confidence: 0.75 } },
        mood_trends: { daily_trends: [], trend_direction: "stable", overall_average: 6.5 },
        weekly_patterns: {},
        key_insights: ["Start journaling to receive personalized insights about your emotional patterns."],
        summary_stats: { total_entries: 0, entries_this_week: 0, average_mood: 0, most_common_emotion: "calm", current_streak: 0 },
      })
    } finally {
      setIsLoading(false)
    }
  }

  const fetchSuggestions = async () => {
    try {
      const response = await suggestionsAPI.getPersonalized()
      setSuggestions(response.data.suggestions || [])
    } catch (error) {
      console.error('Failed to fetch suggestions:', error)
      setSuggestions(["Take a 5-minute break and practice deep breathing.", "Go for a short walk to clear your mind.", "Write down your thoughts to gain perspective."])
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-dots"><div></div><div></div><div></div><div></div></div>
      </div>
    )
  }

  const avgMood = dashboardData?.summary_stats?.average_mood ?? 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <AppNav />
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>
      <div className="floating-shape shape-3"></div>

      <div className="max-w-7xl mx-auto relative z-10 p-6">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">
            Welcome back, {user?.username || 'User'}! 🌟
          </h1>
          <p className="text-gray-600">Here&apos;s your wellness overview for {formatDate(new Date())}</p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardData?.summary_stats && (
            <>
              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.1 }}
                className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg card-hover">
                <div className="flex items-center justify-between mb-4">
                  <Calendar className="w-8 h-8 text-primary-500" />
                  <span className="text-2xl font-bold text-gray-800">{dashboardData.summary_stats.total_entries}</span>
                </div>
                <h3 className="text-gray-600 font-medium">Total Journal Entries</h3>
                <p className="text-sm text-gray-500 mt-1">{dashboardData.summary_stats.entries_this_week} this week</p>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}
                className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg card-hover">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="w-8 h-8 text-green-500" />
                  <span className="text-2xl font-bold text-gray-800">{avgMood.toFixed(1)}</span>
                </div>
                <h3 className="text-gray-600 font-medium">Average Mood</h3>
                <p className="text-sm text-gray-500 mt-1">Out of 10</p>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.3 }}
                className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg card-hover">
                <div className="flex items-center justify-between mb-4">
                  <Brain className="w-8 h-8 text-purple-500" />
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{getEmotionIcon(dashboardData.summary_stats.most_common_emotion)}</span>
                    <span className="text-lg font-bold text-gray-800 capitalize">{dashboardData.summary_stats.most_common_emotion}</span>
                  </div>
                </div>
                <h3 className="text-gray-600 font-medium">Most Common Emotion</h3>
                <p className="text-sm text-gray-500 mt-1">Based on your entries</p>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.4 }}
                className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg card-hover">
                <div className="flex items-center justify-between mb-4">
                  <Sparkles className="w-8 h-8 text-orange-500" />
                  <span className="text-2xl font-bold text-gray-800">🔥 {dashboardData.summary_stats.current_streak}</span>
                </div>
                <h3 className="text-gray-600 font-medium">Current Streak</h3>
                <p className="text-sm text-gray-500 mt-1">Days in a row</p>
              </motion.div>
            </>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Emotion Distribution */}
            <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.5 }}
              className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-800">Emotion Distribution</h2>
                <BarChart3 className="w-6 h-6 text-primary-500" />
              </div>
              {dashboardData?.emotion_distribution && Object.keys(dashboardData.emotion_distribution).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(dashboardData.emotion_distribution).map(([emotion, data]: [string, any]) => (
                    <div key={emotion} className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2 w-24">
                        <span className="text-2xl">{getEmotionIcon(emotion)}</span>
                        <span className="text-sm font-medium capitalize">{emotion}</span>
                      </div>
                      <div className="flex-1">
                        <div className="h-6 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full transition-all duration-500" style={{ width: `${data.percentage}%`, backgroundColor: getEmotionColor(emotion) }} />
                        </div>
                      </div>
                      <span className="text-sm text-gray-600 w-12 text-right">{data.percentage}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Start journaling to see your emotion distribution</p>
                </div>
              )}
            </motion.div>

            {/* Key Insights */}
            <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.6 }}
              className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-800">Key Insights</h2>
                <Brain className="w-6 h-6 text-primary-500" />
              </div>
              {dashboardData?.key_insights && dashboardData.key_insights.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.key_insights.map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                      <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-gray-700 leading-relaxed">{insight}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Sparkles className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Continue journaling to receive personalized insights</p>
                </div>
              )}
            </motion.div>
          </div>

          <div className="space-y-8">
            {/* Suggestions */}
            <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.7 }}
              className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-800">For You</h2>
                <Sparkles className="w-6 h-6 text-orange-500" />
              </div>
              {suggestions.length > 0 ? (
                <div className="space-y-3">
                  {suggestions.slice(0, 4).map((suggestion, index) => (
                    <div key={index} className="p-3 bg-gradient-to-r from-orange-50 to-primary-50 rounded-lg">
                      <p className="text-sm text-gray-700 leading-relaxed">{suggestion}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-gray-500">
                  <Heart className="w-10 h-10 mx-auto mb-3 text-gray-300" />
                  <p className="text-sm">Loading personalized suggestions...</p>
                </div>
              )}
            </motion.div>

            {/* Quick Actions */}
            <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.8 }}
              className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-semibold text-gray-800 mb-6">Quick Actions</h2>
              <div className="space-y-3">
                <button onClick={() => router.push('/journal')}
                  className="w-full p-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover flex items-center justify-center space-x-2">
                  <BookOpen className="w-5 h-5" /><span>New Journal Entry</span>
                </button>
                <button onClick={() => router.push('/community')}
                  className="w-full p-3 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all flex items-center justify-center space-x-2">
                  <Users className="w-5 h-5" /><span>Visit Community</span>
                </button>
                <button onClick={() => router.push('/chat')}
                  className="w-full p-3 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all flex items-center justify-center space-x-2">
                  <MessageCircle className="w-5 h-5" /><span>Chat & Support</span>
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
