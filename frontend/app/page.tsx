'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Calendar, Sparkles, Users, TrendingUp, Zap, Mail, Brain, Target, ArrowRight, Mic } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

export default function Home() {
  const router = useRouter()

  // Session persistence - redirect logged-in users to dashboard
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Use replace() to avoid back button trap
      router.replace('/dashboard')
    }
  }, [router])

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

          {/* Agent Team Section */}
          <div className="mt-20">
            <h2 className="text-4xl font-bold text-center mb-4 text-gray-900 dark:text-white">
              Meet Your AI Agent Team
            </h2>
            <p className="text-center text-gray-600 dark:text-gray-400 mb-16 text-lg">
              Three specialized AI agents working together to supercharge your networking
            </p>

            <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
              <AgentCard
                icon={<Target className="w-12 h-12" />}
                name="Arya"
                role="Event Scout"
                description="Arya scouts networking events that match your interests and business goals. He analyzes your profile and finds perfect opportunities where you can grow your network."
                gradient="from-blue-500 to-cyan-500"
                delay={0.2}
              />
              <AgentCard
                icon={<Mic className="w-12 h-12" />}
                name="Dhwani"
                role="Voice Intelligence"
                description="Dhwani listens to every conversation with state-of-the-art AI. She performs speaker diarization (identifies who's talking), eliminates background noise, and creates accurate transcripts."
                gradient="from-purple-500 to-pink-500"
                delay={0.4}
              />
              <AgentCard
                icon={<Sparkles className="w-12 h-12" />}
                name="Lakshya"
                role="Lead Generator"
                description="Lakshya analyzes your conversations and automatically generates qualified leads. He extracts contact information, identifies business opportunities, and provides actionable insights."
                gradient="from-orange-500 to-red-500"
                delay={0.6}
              />
            </div>
          </div>

          {/* How It Works */}
          <div className="grid md:grid-cols-3 gap-8 mt-20">
            <WorkflowStep
              number="1"
              icon={<Target className="w-6 h-6" />}
              title="Discover Events"
              description="Arya finds events matching your profile"
            />
            <WorkflowStep
              number="2"
              icon={<Mic className="w-6 h-6" />}
              title="Record Conversations"
              description="Dhwani captures and transcribes with precision"
            />
            <WorkflowStep
              number="3"
              icon={<Sparkles className="w-6 h-6" />}
              title="Generate Leads"
              description="Lakshya extracts opportunities automatically"
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

function AgentCard({
  icon,
  name,
  role,
  description,
  gradient,
  delay,
}: {
  icon: React.ReactNode
  name: string
  role: string
  description: string
  gradient: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -8 }}
      className="relative p-8 rounded-3xl glass-effect shadow-xl hover:shadow-2xl transition-all border-2 border-gray-200 dark:border-gray-700"
    >
      <div className={`inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br ${gradient} text-white mb-6 shadow-lg`}>
        {icon}
      </div>
      <h3 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">
        {name}
      </h3>
      <p className={`text-sm font-semibold mb-4 bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
        {role}
      </p>
      <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
        {description}
      </p>
    </motion.div>
  )
}

function WorkflowStep({
  number,
  icon,
  title,
  description,
}: {
  number: string
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="text-center relative">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-900 to-cyan-600 text-white font-bold text-2xl mb-4 shadow-lg">
        {number}
      </div>
      <h4 className="text-xl font-bold mb-2 text-gray-900 dark:text-white flex items-center justify-center gap-2">
        {icon}
        {title}
      </h4>
      <p className="text-gray-600 dark:text-gray-400">{description}</p>
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
