'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Heart, Eye, EyeOff, Mail, Lock, User } from 'lucide-react'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  
  const router = useRouter()
  const { login, setLoading } = useAuthStore()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const validateStep1 = () => {
    if (!formData.email || !formData.username || !formData.password || !formData.confirmPassword) {
      toast.error('Please fill in all required fields')
      return false
    }
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match')
      return false
    }
    
    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters long')
      return false
    }
    
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (currentStep === 1) {
      if (validateStep1()) {
        setCurrentStep(2)
      }
      return
    }

    setIsLoading(true)
    setLoading(true)

    try {
      const { confirmPassword, ...userData } = formData
      const response = await authAPI.register(userData)
      const user = response.data
      
      // Auto login after registration
      const loginResponse = await authAPI.login({
        email: formData.email,
        password: formData.password,
      })
      const { access_token } = loginResponse.data
      
      login(user, access_token)
      toast.success('Welcome to Sereno! 🎉')
      router.push('/onboarding')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed')
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      {/* Background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>
      
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="w-full max-w-md"
      >
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Heart className="w-10 h-10 text-primary-500" />
              <span className="text-3xl font-bold gradient-text">Sereno</span>
            </div>
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">
              {currentStep === 1 ? 'Create Account' : 'Complete Your Profile'}
            </h1>
            <p className="text-gray-600">
              {currentStep === 1 
                ? 'Join our community and start your wellness journey'
                : 'Tell us a bit more about yourself'
              }
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex items-center space-x-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= 1 ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                1
              </div>
              <div className={`w-16 h-1 ${currentStep >= 2 ? 'bg-primary-500' : 'bg-gray-200'}`}></div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= 2 ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                2
              </div>
            </div>
          </div>

          {/* Registration Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {currentStep === 1 ? (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-800 bg-white placeholder-gray-400"
                      placeholder="you@example.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      required
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-800 bg-white placeholder-gray-400"
                      placeholder="johndoe"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-800 bg-white placeholder-gray-400"
                      placeholder="••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-800 bg-white placeholder-gray-400"
                      placeholder="••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-800 bg-white placeholder-gray-400"
                    placeholder="John Doe"
                  />
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  This is optional and helps us personalize your experience
                </p>
              </div>
            )}

            <div className="flex space-x-4">
              {currentStep === 1 && (
                <button
                  type="button"
                  onClick={() => router.push('/auth/login')}
                  className="flex-1 py-3 px-4 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all"
                >
                  Back
                </button>
              )}
              
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 py-3 px-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed btn-hover"
              >
                {isLoading 
                  ? 'Creating Account...' 
                  : currentStep === 1 
                    ? 'Next Step' 
                    : 'Create Account'
                }
              </button>
            </div>
          </form>

          {/* Sign In Link */}
          <div className="mt-8 text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link href="/auth/login" className="text-primary-600 hover:text-primary-500 font-semibold">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
