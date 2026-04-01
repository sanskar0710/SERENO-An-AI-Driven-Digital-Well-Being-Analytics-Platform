'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Heart, ArrowLeft, Eye, MessageCircle, Users, BarChart3, Sparkles } from 'lucide-react'

export default function DemoPage() {
  const demos = [
    {
      title: "AI-Powered Journal Analysis",
      description: "See how our AI analyzes your journal entries for emotional insights",
      icon: <BarChart3 className="w-8 h-8" />,
      features: ["Emotion detection", "Sentiment analysis", "Keyword extraction", "Personalized insights"]
    },
    {
      title: "Community Support",
      description: "Experience the power of community-driven mental wellness support",
      icon: <Users className="w-8 h-8" />,
      features: ["Anonymous posting", "Reactions & comments", "Media sharing", "Moderated environment"]
    },
    {
      title: "Real-time Dashboard",
      description: "Track your emotional well-being with beautiful visualizations",
      icon: <Eye className="w-8 h-8" />,
      features: ["Emotion distribution", "Mood trends", "Weekly patterns", "Well-being score"]
    },
    {
      title: "Personalized Suggestions",
      description: "Get AI-powered recommendations based on your emotional patterns",
      icon: <Sparkles className="w-8 h-8" />,
      features: ["Context-aware suggestions", "Preference-based recommendations", "Activity ideas", "Coping strategies"]
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      {/* Background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>
      <div className="floating-shape shape-3"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-8"
        >
          <Link 
            href="/"
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors mb-8"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Home</span>
          </Link>
          
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Heart className="w-8 h-8 text-primary-500" />
            <h1 className="text-4xl font-bold gradient-text">Sereno Demo</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience the future of mental wellness with our AI-powered platform
          </p>
        </motion.div>

        {/* Demo Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {demos.map((demo, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
              className="bg-white/80 backdrop-blur-lg rounded-2xl p-8 shadow-lg card-hover"
            >
              <div className="flex items-center justify-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-xl flex items-center justify-center text-white">
                  {demo.icon}
                </div>
              </div>
              
              <h3 className="text-2xl font-bold text-gray-800 mb-4">{demo.title}</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">{demo.description}</p>
              
              <div className="space-y-2">
                <h4 className="font-semibold text-gray-700 mb-3">Key Features:</h4>
                <ul className="space-y-2">
                  {demo.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-center"
        >
          <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-12 shadow-lg">
            <h2 className="text-3xl font-bold gradient-text mb-6">Ready to Start Your Journey?</h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of users who have found peace and clarity with Sereno
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/auth/register"
                className="px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-full font-semibold text-lg hover:shadow-lg transition-all btn-hover"
              >
                Create Account
              </Link>
              <Link
                href="/auth/login"
                className="px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-full font-semibold text-lg hover:bg-gray-50 transition-all"
              >
                Sign In
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <footer className="relative z-10 px-6 py-12 bg-gray-50 mt-16">
          <div className="max-w-7xl mx-auto text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Heart className="w-6 h-6 text-primary-500" />
              <span className="text-xl font-bold gradient-text">Sereno</span>
            </div>
            <p className="text-gray-600 mb-2">AI-Driven Digital Well-Being Platform</p>
            <p className="text-sm text-gray-500">© 2024 Sereno. Supporting mental wellness for everyone.</p>
          </div>
        </footer>
      </div>
    </div>
  )
}
