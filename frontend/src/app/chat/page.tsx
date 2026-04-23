'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { Send, Users, MessageCircle, Search } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { chatAPI } from '@/lib/api'
import { formatDateTime, truncateText } from '@/lib/utils'
import { AppNav } from '@/app/dashboard/page'

interface Message {
  id: string
  sender_id: string
  receiver_id: string
  message: string
  timestamp: string
  is_read: boolean
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

export default function ChatPage() {
  const { user } = useAuthStore()
  const router = useRouter()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const response = await chatAPI.getConversations()
      if (Array.isArray(response.data)) {
        setConversations(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchConversations = async () => {
    // Handled by loadConversations
  }

  const fetchMessages = async (userId: string) => {
    try {
      const response = await chatAPI.getMessages(userId)
      setMessages(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Failed to fetch messages:', error)
      setMessages([])
    }
  }

  const handleSelectConversation = (userId: string) => {
    setSelectedConversation(userId)
    fetchMessages(userId)
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return

    try {
      const messageData = {
        receiver_id: selectedConversation,
        message: newMessage.trim(),
        message_type: 'text'
      }

      // In a real app, this would send via WebSocket
      // For demo, we'll just add it to local state
      const newMsg: Message = {
        id: Date.now().toString(),
        sender_id: user?.id || '',
        receiver_id: selectedConversation,
        message: newMessage.trim(),
        timestamp: new Date().toISOString(),
        is_read: false
      }

      setMessages(prev => [...prev, newMsg])
      setNewMessage('')
      
      // Update conversation's last message
      setConversations(prev => prev.map(conv => 
        conv.user_id === selectedConversation 
          ? { ...conv, last_message: newMessage.trim(), last_timestamp: newMsg.timestamp }
          : conv
      ))
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const selectedConvData = conversations.find(conv => conv.user_id === selectedConversation)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <AppNav />
      {/* Background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>
      <div className="floating-shape shape-3"></div>

      <div className="max-w-7xl mx-auto relative z-10 p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold gradient-text mb-2">Chat & Support</h1>
          <p className="text-gray-600">Connect with others on their wellness journey</p>
        </motion.div>

        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-lg overflow-hidden" style={{ height: '600px' }}>
          <div className="flex h-full">
            {/* Conversations List */}
            <div className="w-80 border-r border-gray-200 bg-gray-50 p-4 overflow-y-auto">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Conversations</h2>
              
              {isLoading ? (
                <div className="space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="bg-white p-4 rounded-lg shadow animate-pulse">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gray-200 rounded-full animate-pulse"></div>
                        <div>
                          <div className="h-4 bg-gray-200 rounded w-24 mb-2 animate-pulse"></div>
                          <div className="h-3 bg-gray-200 rounded w-32 animate-pulse"></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : conversations.length === 0 ? (
                <div className="text-center py-8">
                  <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500">No conversations yet</p>
                  <p className="text-sm text-gray-400">Start a conversation from the community page</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {conversations.map((conv) => (
                    <div
                      key={conv.user_id}
                      onClick={() => handleSelectConversation(conv.user_id)}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        selectedConversation === conv.user_id
                          ? 'bg-primary-100 border-primary-300'
                          : 'bg-white hover:bg-gray-50 border border-gray-200'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                          <Users className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-800">{conv.username}</p>
                          <p className="text-sm text-gray-500 truncate">{conv.last_message}</p>
                        </div>
                      </div>
                      {conv.unread_count > 0 && (
                        <div className="w-3 h-3 bg-red-500 rounded-full flex items-center justify-center">
                          <span className="text-xs text-white font-bold">{conv.unread_count}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
              {selectedConvData ? (
                <>
                  {/* Chat Header */}
                  <div className="bg-white border-b border-gray-200 p-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{selectedConvData.username}</p>
                        <p className="text-sm text-gray-500">Active now</p>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-xs lg:max-w-md ${message.sender_id === user?.id ? 'order-2' : 'order-1'}`}>
                          <div className={`flex items-end space-x-2 ${message.sender_id === user?.id ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center ${message.sender_id === user?.id ? 'order-2' : 'order-1'}`}>
                              <Users className="w-4 h-4 text-white" />
                            </div>
                            <div className={`px-4 py-2 rounded-lg ${message.sender_id === user?.id ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-800'}`}>
                              <p className="text-sm">{message.message}</p>
                              <p className="text-xs opacity-70 mt-1">{formatDateTime(message.timestamp)}</p>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  {/* Message Input */}
                  <div className="border-t border-gray-200 p-4">
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            handleSendMessage()
                          }
                        }}
                        placeholder="Type a message..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                      <button
                        onClick={handleSendMessage}
                        disabled={!newMessage.trim()}
                        className="p-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-full hover:shadow-lg transition-all disabled:opacity-50"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">Select a Conversation</h3>
                    <p className="text-gray-500">Choose a conversation from the list to start messaging</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
