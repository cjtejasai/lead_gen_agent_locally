'use client'

import { motion } from 'framer-motion'
import { Calendar, Sparkles, Users, TrendingUp, Zap, Mail, Brain, Target, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          {/* Logo/Brand */}
          <div className="flex items-center justify-center mb-8">
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-900 to-cyan-600 rounded-full blur-3xl opacity-30"></div>
              <Image
                src="/lyncsea-logo.png"
                alt="Lyncsea"
                width={100}
                height={100}
                className="relative rounded-2xl shadow-2xl"
              />
            </motion.div>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-[#1e3a8a] via-[#0891b2] to-[#1e3a8a]">
            Never Miss a Connection Again
          </h1>

          <p className="text-2xl text-gray-600 dark:text-gray-300 mb-4">
            Turn Event Conversations Into Valuable Connections
          </p>

          <p className="text-lg text-gray-500 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Record, analyze, and discover collaboration opportunities automatically
            with AI-powered lead generation at networking events.
          </p>

          {/* CTA Buttons */}
          <div className="flex gap-4 justify-center mb-16">
            <Link href="/dashboard">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-full font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl transition-shadow"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>

            <Link href="/demo">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-full font-semibold border-2 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
              >
                Watch Demo
              </motion.button>
            </Link>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-8 mt-20">
            <FeatureCard
              icon={<Zap className="w-8 h-8" />}
              title="Smart Recording"
              description="Capture conversations at events with our wearable pendant device"
              delay={0.2}
            />
            <FeatureCard
              icon={<Sparkles className="w-8 h-8" />}
              title="AI Analysis"
              description="LLM-powered agents extract interests, needs, and opportunities"
              delay={0.4}
            />
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Auto Matching"
              description="Discover perfect collaboration opportunities with intelligent matching"
              delay={0.6}
            />
          </div>

          {/* Stats Section */}
          <div className="grid md:grid-cols-3 gap-8 mt-20 py-12 border-y border-gray-200 dark:border-gray-800">
            <StatCard value="10x" label="Faster Networking" />
            <StatCard value="95%" label="Match Accuracy" />
            <StatCard value="500+" label="Connections Made" />
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
  delay,
}: {
  icon: React.ReactNode
  title: string
  description: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -8 }}
      className="p-8 rounded-2xl glass-effect shadow-lg hover:shadow-xl transition-all"
    >
      <div className="text-blue-600 mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-400">{description}</p>
    </motion.div>
  )
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-4xl font-bold text-gradient mb-2">{value}</div>
      <div className="text-gray-600 dark:text-gray-400">{label}</div>
    </div>
  )
}
