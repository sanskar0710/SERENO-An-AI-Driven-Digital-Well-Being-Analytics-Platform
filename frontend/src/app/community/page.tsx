'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Heart, MessageCircle, Users, Plus, Search, Filter, Share2, Eye } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { communityAPI } from '@/lib/api'
import { formatDate, formatDateTime, truncateText } from '@/lib/utils'
import { AppNav } from '@/app/dashboard/page'
import toast from 'react-hot-toast'

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
  }>
  is_edited: boolean
}

export default function CommunityPage() {
  const { user } = useAuthStore()
  const [posts, setPosts] = useState<CommunityPost[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTag, setSelectedTag] = useState('')
  const [showNewPost, setShowNewPost] = useState(false)
  const [newPost, setNewPost] = useState({
    title: '',
    text: '',
    anonymous: false,
    tags: ''
  })

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const response = await communityAPI.getPosts()
      setPosts(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Failed to fetch community posts:', error)
      setPosts([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreatePost = async () => {
    if (!newPost.text.trim()) return

    try {
      const postData = {
        title: newPost.title,
        text: newPost.text,
        anonymous: newPost.anonymous,
        tags: newPost.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      }

      const response = await communityAPI.createPost(postData)
      setPosts([response.data, ...posts])
      toast.success('Story shared with the community! 💛')
      
      // Reset form
      setNewPost({ title: '', text: '', anonymous: false, tags: '' })
      setShowNewPost(false)
    } catch (error) {
      console.error('Failed to create post:', error)
      toast.error('Failed to share story. Please try again.')
    }
  }

  const handleReact = async (postId: string, reactionType: string) => {
    try {
      await communityAPI.addReaction(postId, { reaction_type: reactionType })
      // Update local state
      setPosts(posts.map(post => 
        post.id === postId 
          ? {
              ...post,
              reactions: {
                ...post.reactions,
                [reactionType]: (post.reactions[reactionType] || 0) + 1
              }
            }
          : post
      ))
    } catch (error) {
      console.error('Failed to add reaction:', error)
    }
  }

  const filteredPosts = posts.filter(post => {
    const matchesSearch = post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesTag = !selectedTag || post.tags.includes(selectedTag)
    return matchesSearch && matchesTag
  })

  const popularTags = [...new Set(posts.flatMap(post => post.tags))].slice(0, 10)

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <AppNav />
      {/* Background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>

      <div className="max-w-6xl mx-auto relative z-10 p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">Community</h1>
              <p className="text-gray-600">
                Share your experiences and connect with others on similar journeys
              </p>
            </div>
            <button
              onClick={() => setShowNewPost(true)}
              className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Share Your Story</span>
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
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={selectedTag}
                onChange={(e) => setSelectedTag(e.target.value)}
                className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none"
              >
                <option value="">All Tags</option>
                {popularTags.map(tag => (
                  <option key={tag} value={tag}>#{tag}</option>
                ))}
              </select>
            </div>
          </div>
        </motion.div>

        {/* New Post Modal */}
        {showNewPost && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50"
            onClick={() => setShowNewPost(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold mb-6 gradient-text">Share Your Story</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title (optional)
                  </label>
                  <input
                    type="text"
                    value={newPost.title}
                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                    placeholder="Give your story a title..."
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Story
                  </label>
                  <textarea
                    value={newPost.text}
                    onChange={(e) => setNewPost({ ...newPost, text: e.target.value })}
                    placeholder="Share your experience, thoughts, or feelings..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={newPost.tags}
                    onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
                    placeholder="gratitude, recovery, mindfulness, support"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="anonymous"
                    checked={newPost.anonymous}
                    onChange={(e) => setNewPost({ ...newPost, anonymous: e.target.checked })}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="anonymous" className="ml-2 text-sm text-gray-700">
                    Post anonymously
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-4 mt-8">
                <button
                  onClick={() => setShowNewPost(false)}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreatePost}
                  disabled={!newPost.text.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  Share Story
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Community Posts */}
        <div className="space-y-6">
          {filteredPosts.length > 0 ? (
            filteredPosts.map((post, index) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="bg-white/80 backdrop-blur-lg rounded-xl p-6 shadow-lg card-hover"
              >
                {/* Post Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">
                        {post.anonymous ? 'Anonymous' : post.username}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDateTime(post.timestamp)}
                      </p>
                    </div>
                  </div>
                  {post.is_edited && (
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      Edited
                    </span>
                  )}
                </div>

                {/* Post Content */}
                {post.title && (
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">
                    {post.title}
                  </h3>
                )}
                
                <div className="mb-4">
                  <p className="text-gray-700 leading-relaxed">
                    {truncateText(post.text, 400)}
                    {post.text.length > 400 && (
                      <button className="text-primary-600 hover:text-primary-500 ml-2">
                        Read more
                      </button>
                    )}
                  </p>
                </div>

                {/* Tags */}
                {post.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {post.tags.map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="px-3 py-1 bg-gradient-to-r from-primary-100 to-secondary-100 text-primary-700 rounded-full text-sm"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Reactions */}
                <div className="flex items-center justify-between border-t pt-4">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => handleReact(post.id, 'like')}
                      className="flex items-center space-x-1 text-gray-600 hover:text-red-500 transition-colors"
                    >
                      <Heart className="w-5 h-5" />
                      <span className="text-sm">{post.reactions.like || 0}</span>
                    </button>
                    <button
                      onClick={() => handleReact(post.id, 'support')}
                      className="flex items-center space-x-1 text-gray-600 hover:text-blue-500 transition-colors"
                    >
                      <Users className="w-5 h-5" />
                      <span className="text-sm">{post.reactions.support || 0}</span>
                    </button>
                    <button className="flex items-center space-x-1 text-gray-600 hover:text-green-500 transition-colors">
                      <MessageCircle className="w-5 h-5" />
                      <span className="text-sm">{post.comments.length}</span>
                    </button>
                  </div>
                  <button className="flex items-center space-x-1 text-gray-600 hover:text-primary-500 transition-colors">
                    <Share2 className="w-5 h-5" />
                    <span className="text-sm">Share</span>
                  </button>
                </div>
              </motion.div>
            ))
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="bg-white/80 backdrop-blur-lg rounded-xl p-12 shadow-lg text-center"
            >
              <Users className="w-16 h-16 mx-auto mb-6 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No posts yet</h3>
              <p className="text-gray-600 mb-6">
                Be the first to share your story with the community
              </p>
              <button
                onClick={() => setShowNewPost(true)}
                className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover inline-flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>Share First Story</span>
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
