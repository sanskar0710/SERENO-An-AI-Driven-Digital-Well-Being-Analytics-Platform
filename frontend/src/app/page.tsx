'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Heart, Brain, Users, MessageCircle, Sparkles, ArrowRight } from 'lucide-react'

export default function HomePage() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Floating background shapes */}
      <div className="floating-shape shape-1"></div>
      <div className="floating-shape shape-2"></div>
      <div className="floating-shape shape-3"></div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Heart className="w-8 h-8 text-primary-500" />
            <span className="text-2xl font-bold gradient-text">Sereno</span>
          </div>
          <div className="flex items-center space-x-6">
            <Link href="/auth/login" className="text-gray-600 hover:text-primary-600 transition-colors">
              Login
            </Link>
            <Link 
              href="/auth/register" 
              className="px-6 py-2 bg-primary-500 text-white rounded-full hover:bg-primary-600 transition-colors btn-hover"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Find Your Inner Peace</span>
              <br />
              <span className="text-gray-800">with AI Support</span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Sereno is your AI-powered digital well-being companion. Reflect on your thoughts, 
              receive personalized insights, and connect with a supportive community dedicated to mental wellness.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link 
                href="/auth/register"
                className="px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-full font-semibold text-lg hover:shadow-lg transition-all btn-hover flex items-center space-x-2"
              >
                <span>Start Your Journey</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              
              <Link 
                href="/demo"
                className="px-8 py-4 border-2 border-primary-300 text-primary-600 rounded-full font-semibold text-lg hover:bg-primary-50 transition-all"
              >
                View Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 px-6 py-20 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4 gradient-text">How Sereno Helps You Thrive</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Discover the features that make Sereno your perfect mental wellness companion
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white rounded-2xl p-8 shadow-lg card-hover"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-xl flex items-center justify-center mb-6">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-800">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-3xl p-12 text-white"
          >
            <Sparkles className="w-16 h-16 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">Ready to Start Your Wellness Journey?</h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of users who have found peace and clarity with Sereno
            </p>
            <Link 
              href="/auth/register"
              className="inline-block px-8 py-4 bg-white text-primary-600 rounded-full font-semibold text-lg hover:bg-gray-100 transition-all btn-hover"
            >
              Get Started Free
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-12 bg-gray-50">
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
  )
}

const features = [
  {
    icon: Brain,
    title: "AI-Powered Insights",
    description: "Get personalized emotional analysis and insights based on your daily reflections using advanced NLP technology."
  },
  {
    icon: Heart,
    title: "Daily Journaling",
    description: "Express your thoughts and feelings in a safe, private space designed to promote self-reflection and emotional awareness."
  },
  {
    icon: Users,
    title: "Supportive Community",
    description: "Connect with others on similar journeys, share experiences, and receive encouragement from a caring community."
  },
  {
    icon: MessageCircle,
    title: "Real-time Chat",
    description: "Engage in meaningful conversations with community members through our secure real-time messaging system."
  },
  {
    icon: Sparkles,
    title: "Personalized Suggestions",
    description: "Receive tailored recommendations for activities and coping strategies based on your emotional patterns and preferences."
  },
  {
    icon: Heart,
    title: "Well-being Tracking",
    description: "Monitor your emotional trends and progress over time with beautiful visualizations and comprehensive insights."
  }
]
