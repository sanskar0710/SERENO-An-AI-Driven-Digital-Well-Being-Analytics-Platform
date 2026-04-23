import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  id: string
  email: string
  username: string
  full_name?: string
  preferences: {
    relaxing_activities: string[]
    hobbies: string[]
    stress_triggers: string[]
    music_preferences: string[]
    preferred_activities: string[]
    disliked_environments: string[]
    time_of_day_preference?: string
  }
  created_at: string
  is_active: boolean
  profile_picture?: string
  bio?: string
  anonymous_mode: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  _hasHydrated: boolean
  login: (user: User, token: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
  setHasHydrated: (state: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      _hasHydrated: false,

      setHasHydrated: (state) => set({ _hasHydrated: state }),
      
      login: (user, token) => {
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        })
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', token)
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
        }
      },
      
      updateUser: (userData) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData }
          })
        }
      },
      
      setLoading: (loading) => {
        set({ isLoading: loading })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => {
        if (typeof window !== 'undefined') {
          return localStorage
        }
        // SSR fallback - noop storage
        return {
          getItem: () => null,
          setItem: () => {},
          removeItem: () => {},
        }
      }),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    }
  )
)

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
  media_files: string[]
}

interface JournalState {
  entries: JournalEntry[]
  currentEntry: JournalEntry | null
  isLoading: boolean
  setEntries: (entries: JournalEntry[]) => void
  addEntry: (entry: JournalEntry) => void
  updateEntry: (entryId: string, entry: Partial<JournalEntry>) => void
  deleteEntry: (entryId: string) => void
  setCurrentEntry: (entry: JournalEntry | null) => void
  setLoading: (loading: boolean) => void
}

export const useJournalStore = create<JournalState>((set, get) => ({
  entries: [],
  currentEntry: null,
  isLoading: false,
  setEntries: (entries) => set({ entries }),
  addEntry: (entry) => {
    const currentEntries = get().entries
    set({ entries: [entry, ...currentEntries] })
  },
  updateEntry: (entryId, updatedData) => {
    const currentEntries = get().entries
    const updatedEntries = currentEntries.map(entry =>
      entry.id === entryId ? { ...entry, ...updatedData } : entry
    )
    set({ entries: updatedEntries })
  },
  deleteEntry: (entryId) => {
    const currentEntries = get().entries
    const filteredEntries = currentEntries.filter(entry => entry.id !== entryId)
    set({ entries: filteredEntries })
  },
  setCurrentEntry: (entry) => set({ currentEntry: entry }),
  setLoading: (loading) => set({ isLoading: loading }),
}))

interface CommunityPost {
  id: string
  user_id: string
  username: string
  anonymous: boolean
  title?: string
  text: string
  media_files: string[]
  tags: string[]
  timestamp: string
  reactions: Record<string, number>
  comments: Array<{
    id: string
    user_id: string
    username: string
    anonymous: boolean
    text: string
    timestamp: string
    reactions: Record<string, number>
    is_edited: boolean
    edited_at?: string
  }>
  is_edited: boolean
  edited_at?: string
}

interface CommunityState {
  posts: CommunityPost[]
  currentPost: CommunityPost | null
  isLoading: boolean
  setPosts: (posts: CommunityPost[]) => void
  addPost: (post: CommunityPost) => void
  updatePost: (postId: string, post: Partial<CommunityPost>) => void
  deletePost: (postId: string) => void
  setCurrentPost: (post: CommunityPost | null) => void
  setLoading: (loading: boolean) => void
}

export const useCommunityStore = create<CommunityState>((set, get) => ({
  posts: [],
  currentPost: null,
  isLoading: false,
  setPosts: (posts) => set({ posts }),
  addPost: (post) => {
    const currentPosts = get().posts
    set({ posts: [post, ...currentPosts] })
  },
  updatePost: (postId, updatedData) => {
    const currentPosts = get().posts
    const updatedPosts = currentPosts.map(post =>
      post.id === postId ? { ...post, ...updatedData } : post
    )
    set({ posts: updatedPosts })
  },
  deletePost: (postId) => {
    const currentPosts = get().posts
    const filteredPosts = currentPosts.filter(post => post.id !== postId)
    set({ posts: filteredPosts })
  },
  setCurrentPost: (post) => set({ currentPost: post }),
  setLoading: (loading) => set({ isLoading: loading }),
}))

interface ChatMessage {
  id: string
  sender_id: string
  receiver_id: string
  message: string
  timestamp: string
  is_read: boolean
  message_type: string
  media_url?: string
  reply_to?: string
}

interface Conversation {
  user_id: string
  username: string
  full_name?: string
  profile_picture?: string
  last_message: string
  last_timestamp: string
  unread_count: number
}

interface ChatState {
  conversations: Conversation[]
  currentMessages: ChatMessage[]
  activeConversation: string | null
  isLoading: boolean
  setConversations: (conversations: Conversation[]) => void
  setCurrentMessages: (messages: ChatMessage[]) => void
  setActiveConversation: (userId: string | null) => void
  addMessage: (message: ChatMessage) => void
  updateMessage: (messageId: string, message: Partial<ChatMessage>) => void
  setLoading: (loading: boolean) => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentMessages: [],
  activeConversation: null,
  isLoading: false,
  setConversations: (conversations) => set({ conversations }),
  setCurrentMessages: (messages) => set({ currentMessages: messages }),
  setActiveConversation: (userId) => set({ activeConversation: userId }),
  addMessage: (message) => {
    const currentMessages = get().currentMessages
    set({ currentMessages: [...currentMessages, message] })
  },
  updateMessage: (messageId, updatedData) => {
    const currentMessages = get().currentMessages
    const updatedMessages = currentMessages.map(msg =>
      msg.id === messageId ? { ...msg, ...updatedData } : msg
    )
    set({ currentMessages: updatedMessages })
  },
  setLoading: (loading) => set({ isLoading: loading }),
}))

interface Suggestion {
  text: string
  type: 'emotion' | 'preference' | 'general'
  priority: 'high' | 'medium' | 'low'
}

interface SuggestionsState {
  suggestions: Suggestion[]
  dailyActivity: string | null
  quickTip: string | null
  isLoading: boolean
  setSuggestions: (suggestions: Suggestion[]) => void
  setDailyActivity: (activity: string | null) => void
  setQuickTip: (tip: string | null) => void
  setLoading: (loading: boolean) => void
}

export const useSuggestionsStore = create<SuggestionsState>((set) => ({
  suggestions: [],
  dailyActivity: null,
  quickTip: null,
  isLoading: false,
  setSuggestions: (suggestions) => set({ suggestions }),
  setDailyActivity: (activity) => set({ dailyActivity: activity }),
  setQuickTip: (tip) => set({ quickTip: tip }),
  setLoading: (loading) => set({ isLoading: loading }),
}))
