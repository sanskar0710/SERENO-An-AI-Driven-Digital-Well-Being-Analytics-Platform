'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Heart, ArrowRight, Check } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { authAPI } from '@/lib/api'
import toast from 'react-hot-toast'

export default function OnboardingPage() {
  const { user, updateUser } = useAuthStore()
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [preferences, setPreferences] = useState({
    relaxing_activities: [] as string[],
    hobbies: [] as string[],
    stress_triggers: [] as string[],
    music_preferences: [] as string[],
    preferred_activities: [] as string[],
    disliked_environments: [] as string[],
    time_of_day_preference: ''
  })

  const totalSteps = 6

  const relaxingOptions = ['Music', 'Walking', 'Reading', 'Meditation', 'Exercise', 'Nature', 'Art', 'Cooking', 'Gardening', 'Yoga']
  const hobbyOptions = ['Gaming', 'Sports', 'Writing', 'Photography', 'Travel', 'Cooking', 'Music', 'Art', 'Dancing', 'Movies']
  const stressTriggers = ['Deadlines', 'Crowds', 'Public Speaking', 'Traffic', 'Work Pressure', 'Family Issues', 'Financial Stress', 'Health Concerns']
  const musicOptions = ['Classical', 'Jazz', 'Pop', 'Rock', 'Electronic', 'Ambient', 'Nature Sounds', 'Podcasts', 'Lo-fi', 'Acoustic']
  const activityOptions = ['Indoors', 'Outdoors', 'Social', 'Solo', 'Active', 'Creative', 'Learning', 'Relaxing', 'Adventurous', 'Routine']
  const dislikedEnvironments = ['Crowded places', 'Loud noises', 'Messy spaces', 'Extreme temperatures', 'Bright lights', 'Strong smells', 'High pressure', 'Unfamiliar places']
  const timeOptions = ['Morning', 'Afternoon', 'Evening', 'Night']

  const toggleSelection = (category: string, value: string) => {
    setPreferences(prev => {
      const current = prev[category as keyof typeof prev] as string[]
      if (current.includes(value)) {
        return {
          ...prev,
          [category]: current.filter(item => item !== value)
        }
      } else {
        return {
          ...prev,
          [category]: [...current, value]
        }
      }
    })
  }

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = async () => {
    try {
      // Save preferences to backend
      await authAPI.updateMe({ preferences })
      // Update local store
      updateUser({ preferences } as any)
      toast.success('Onboarding completed! 🎉')
      router.push('/dashboard')
    } catch (error) {
      console.error('Failed to save preferences:', error)
      // Still navigate even if save fails - preferences are in local state
      updateUser({ preferences } as any)
      toast.success('Preferences saved locally! 🎉')
      router.push('/dashboard')
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold gradient-text mb-4">What helps you relax?</h2>
              <p className="text-gray-600">Choose activities that help you unwind and de-stress</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {relaxingOptions.map(option => (
                <button
                  key={option}
                  onClick={() => toggleSelection('relaxing_activities', option)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.relaxing_activities.includes(option)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </motion.div>
        )

      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold gradient-text mb-4">What are your hobbies?</h2>
              <p className="text-gray-600">Tell us about activities you enjoy in your free time</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {hobbyOptions.map(option => (
                <button
                  key={option}
                  onClick={() => toggleSelection('hobbies', option)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.hobbies.includes(option)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </motion.div>
        )

      case 3:
        return (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold gradient-text mb-4">What usually causes stress?</h2>
              <p className="text-gray-600">Understanding your stress triggers helps us provide better support</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {stressTriggers.map(option => (
                <button
                  key={option}
                  onClick={() => toggleSelection('stress_triggers', option)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.stress_triggers.includes(option)
                      ? 'border-accent-500 bg-accent-50 text-accent-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </motion.div>
        )

      case 4:
        return (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold gradient-text mb-4">Music Preferences</h2>
              <p className="text-gray-600">What types of music help you feel better?</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {musicOptions.map(option => (
                <button
                  key={option}
                  onClick={() => toggleSelection('music_preferences', option)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.music_preferences.includes(option)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </motion.div>
        )

      case 5:
        return (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold gradient-text mb-4">Preferred Activities</h2>
              <p className="text-gray-600">What types of activities do you prefer?</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {activityOptions.map(option => (
                <button
                  key={option}
                  onClick={() => toggleSelection('preferred_activities', option)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.preferred_activities.includes(option)
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </motion.div>
        )

      case 6:
        return (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold gradient-text mb-4">Disliked Environments</h2>
              <p className="text-gray-600">What environments do you prefer to avoid?</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {dislikedEnvironments.map(option => (
                <button
                  key={option}
                  onClick={() => toggleSelection('disliked_environments', option)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.disliked_environments.includes(option)
                      ? 'border-accent-500 bg-accent-50 text-accent-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Preferred Time of Day</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {timeOptions.map(option => (
                  <button
                    key={option}
                    onClick={() => setPreferences(prev => ({ ...prev, time_of_day_preference: option }))}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      preferences.time_of_day_preference === option
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300 text-gray-800 bg-white'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      {/* Background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>
      <div className="floating-shape shape-3"></div>

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Heart className="w-8 h-8 text-primary-500" />
            <span className="text-3xl font-bold gradient-text">Sereno</span>
          </div>
          <h1 className="text-2xl font-semibold text-gray-800 mb-2">Welcome to Your Wellness Journey</h1>
          <p className="text-gray-600">Let's personalize your experience</p>
        </motion.div>

        {/* Progress Bar */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-600">Step {currentStep} of {totalSteps}</span>
            <span className="text-sm text-gray-600">{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-primary-500 to-secondary-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / totalSteps) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        {/* Step Content */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 mb-8"
        >
          {renderStep()}
        </motion.div>

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-center"
        >
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {currentStep === totalSteps ? (
            <button
              onClick={handleComplete}
              className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover flex items-center space-x-2"
            >
              <span>Complete Setup</span>
              <Check className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-lg transition-all btn-hover flex items-center space-x-2"
            >
              <span>Next Step</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          )}
        </motion.div>

        {/* Skip for now */}
        <div className="text-center mt-8">
          <Link
            href="/dashboard"
            className="text-gray-500 hover:text-gray-700 underline text-sm"
          >
            Skip for now
          </Link>
        </div>
      </div>
    </div>
  )
}
