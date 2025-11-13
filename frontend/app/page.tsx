'use client'

import { motion } from 'framer-motion'
import { Calendar, Sparkles, Users, TrendingUp, Zap, Mail, Brain, Target, ArrowRight, Mic } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Navigation Header */}
      <nav className="border-b border-gray-200 dark:border-gray-800 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/lyncsea-logo.png"
                alt="Lyncsea"
                width={80}
                height={80}
                className="rounded-lg"
              />
              <span className="text-3xl font-bold text-gradient tracking-tight">Lyncsea</span>
            </Link>

            <div className="flex items-center gap-4">
              <Link href="/login">
                <button className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 font-medium transition-colors">
                  Log In
                </button>
              </Link>
              <Link href="/signup">
                <button className="px-6 py-2 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-full font-semibold hover:shadow-lg transition-shadow">
                  Sign Up
                </button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

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
            <Link href="/signup">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-full font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl transition-shadow"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>

            <Link href="/login">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-full font-semibold border-2 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
              >
                Log In
              </motion.button>
            </Link>
          </div>

          {/* Feature Cards - Two Main Features */}
          <div className="grid md:grid-cols-2 gap-12 mt-20 max-w-5xl mx-auto">
            <FeatureCard
              icon={<Calendar className="w-10 h-10" />}
              title="AI Event Discovery"
              description="Our AI agent analyzes your profile, interests, and business goals to discover perfect networking events. Get personalized recommendations that match your professional needs."
              delay={0.2}
            />
            <FeatureCard
              icon={<Mic className="w-10 h-10" />}
              title="Smart Recording & Lead Gen"
              description="Record conversations at events with Bluetooth device. Our AI transcribes, identifies speakers, extracts business opportunities, and generates qualified leads automatically."
              delay={0.4}
            />
          </div>

          {/* Sub-Features */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <SubFeature
              icon={<Brain className="w-6 h-6" />}
              title="AI-Powered Matching"
              description="Automatically matches people's needs with your offerings"
            />
            <SubFeature
              icon={<Users className="w-6 h-6" />}
              title="Speaker Diarization"
              description="Identifies and separates different speakers in conversations"
            />
            <SubFeature
              icon={<Target className="w-6 h-6" />}
              title="Lead Generation"
              description="Extracts actionable leads with contact info and follow-up insights"
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
      className="p-10 rounded-3xl glass-effect shadow-xl hover:shadow-2xl transition-all border-2 border-blue-100 dark:border-blue-900/30"
    >
      <div className="text-blue-600 mb-6">{icon}</div>
      <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-lg leading-relaxed">{description}</p>
    </motion.div>
  )
}

function SubFeature({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="text-center p-6 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 mb-4">
        {icon}
      </div>
      <h4 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
        {title}
      </h4>
      <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
    </div>
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
