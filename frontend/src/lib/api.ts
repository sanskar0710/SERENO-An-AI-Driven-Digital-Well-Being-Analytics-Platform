import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      const path = window.location.pathname
      // Don't redirect if already on auth pages
      if (!path.startsWith('/auth') && !path.startsWith('/demo') && path !== '/') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/auth/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (userData: any) => api.post('/api/auth/register', userData),
  login: (credentials: any) => api.post('/api/auth/login', credentials),
  getMe: () => api.get('/api/auth/me'),
  updateMe: (userData: any) => api.put('/api/auth/me', userData),
}

export const journalAPI = {
  createEntry: (entryData: any) => api.post('/api/journal/entries', entryData),
  getEntries: (params?: any) => api.get('/api/journal/entries', { params }),
  getEntry: (entryId: string) => api.get(`/api/journal/entries/${entryId}`),
  updateEntry: (entryId: string, entryData: any) => api.put(`/api/journal/entries/${entryId}`, entryData),
  deleteEntry: (entryId: string) => api.delete(`/api/journal/entries/${entryId}`),
  analyzeText: (text: string, userPreferences?: any) => api.post('/api/journal/analyze', { text, user_preferences: userPreferences }),
  getStats: () => api.get('/api/journal/stats'),
}

export const communityAPI = {
  createPost: (postData: any) => api.post('/api/community/posts', postData),
  getPosts: (params?: any) => api.get('/api/community/posts', { params }),
  getPost: (postId: string) => api.get(`/api/community/posts/${postId}`),
  updatePost: (postId: string, postData: any) => api.put(`/api/community/posts/${postId}`, postData),
  deletePost: (postId: string) => api.delete(`/api/community/posts/${postId}`),
  addReaction: (postId: string, reaction: any) => api.post(`/api/community/posts/${postId}/reactions`, reaction),
  addComment: (postId: string, comment: any) => api.post(`/api/community/posts/${postId}/comments`, comment),
  updateComment: (postId: string, commentId: string, comment: any) => api.put(`/api/community/posts/${postId}/comments/${commentId}`, comment),
  deleteComment: (postId: string, commentId: string) => api.delete(`/api/community/posts/${postId}/comments/${commentId}`),
  uploadMedia: (postId: string, formData: FormData) => api.post(`/api/community/posts/${postId}/media`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}

export const chatAPI = {
  getConversations: () => api.get('/api/chat/conversations'),
  getMessages: (userId: string, params?: any) => api.get(`/api/chat/messages/${userId}`, { params }),
  markAsRead: (messageId: string) => api.post(`/api/chat/messages/${messageId}/read`),
  getOnlineUsers: () => api.get('/api/chat/online-users'),
}

export const suggestionsAPI = {
  getPersonalized: () => api.get('/api/suggestions/personalized'),
  analyzeMood: (text: string) => api.post('/api/suggestions/analyze-mood', { text }),
  getDailyActivity: () => api.get('/api/suggestions/daily-activity'),
}

export const insightsAPI = {
  getDashboard: () => api.get('/api/insights/dashboard'),
  getEmotionHistory: (days?: number) => api.get('/api/insights/emotion-history', { params: { days } }),
  getWellbeingScore: () => api.get('/api/insights/wellbeing-score'),
}

export default api
