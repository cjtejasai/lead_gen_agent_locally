'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Upload,
  Sparkles,
  Users,
  TrendingUp,
  Settings,
  Bell,
  Search,
} from 'lucide-react'
import Link from 'next/link'

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Navigation Header */}
      <nav className="border-b border-gray-200 dark:border-gray-800 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2">
              <Sparkles className="w-8 h-8 text-purple-600" />
              <span className="text-2xl font-bold text-gradient">Ayka</span>
            </Link>

            {/* Search */}
            <div className="flex-1 max-w-xl mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search recordings, matches, interests..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 rounded-full border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors relative">
                <Bell className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-pink-500 rounded-full"></span>
              </button>
              <Link href="/settings">
                <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors">
                  <Settings className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                </button>
              </Link>
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center text-white font-semibold">
                JD
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Upload className="w-6 h-6" />}
            label="Total Recordings"
            value="12"
            change="+3 this week"
            positive
          />
          <StatCard
            icon={<Users className="w-6 h-6" />}
            label="Active Matches"
            value="24"
            change="+8 new"
            positive
          />
          <StatCard
            icon={<Sparkles className="w-6 h-6" />}
            label="Interests Tracked"
            value="45"
            change="+12 new"
            positive
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6" />}
            label="Connections Made"
            value="8"
            change="+2 this week"
            positive
          />
        </div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Recent Activity & Upload */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-effect rounded-2xl p-8 shadow-lg"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                Upload Recording
              </h2>

              <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-12 text-center hover:border-purple-400 dark:hover:border-purple-600 transition-colors cursor-pointer group">
                <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400 group-hover:text-purple-600 transition-colors" />
                <p className="text-lg font-medium mb-2 text-gray-900 dark:text-white">
                  Drop your recording here or click to browse
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Supports MP3, WAV, M4A, MP4 (Max 500MB)
                </p>
              </div>

              <div className="mt-4 flex items-center gap-4">
                <button className="flex-1 py-3 px-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full font-semibold hover:shadow-lg transition-shadow">
                  Start Processing
                </button>
                <button className="px-6 py-3 border border-gray-200 dark:border-gray-700 rounded-full font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  Cancel
                </button>
              </div>
            </motion.div>

            {/* Recent Recordings */}
            <RecentRecordings />
          </div>

          {/* Right Column - Matches Feed */}
          <div className="space-y-6">
            <MatchesFeed />
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  change,
  positive,
}: {
  icon: React.ReactNode
  label: string
  value: string
  change: string
  positive: boolean
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-effect rounded-2xl p-6 shadow-lg"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl text-purple-600">
          {icon}
        </div>
      </div>
      <div className="text-3xl font-bold mb-1 text-gray-900 dark:text-white">
        {value}
      </div>
      <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
        {label}
      </div>
      <div
        className={`text-sm font-medium ${
          positive ? 'text-green-600' : 'text-gray-500'
        }`}
      >
        {change}
      </div>
    </motion.div>
  )
}

function RecentRecordings() {
  const recordings = [
    {
      id: 1,
      title: 'Tech Conference 2024',
      date: '2 hours ago',
      status: 'Processing',
      progress: 65,
    },
    {
      id: 2,
      title: 'Startup Meetup',
      date: '1 day ago',
      status: 'Completed',
      matches: 5,
    },
    {
      id: 3,
      title: 'Investment Summit',
      date: '3 days ago',
      status: 'Completed',
      matches: 12,
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass-effect rounded-2xl p-6 shadow-lg"
    >
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
        Recent Recordings
      </h3>
      <div className="space-y-4">
        {recordings.map((recording) => (
          <div
            key={recording.id}
            className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700 transition-colors cursor-pointer"
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-gray-900 dark:text-white">
                {recording.title}
              </h4>
              <span className="text-sm text-gray-500">{recording.date}</span>
            </div>
            <div className="flex items-center justify-between">
              <span
                className={`text-sm ${
                  recording.status === 'Processing'
                    ? 'text-yellow-600'
                    : 'text-green-600'
                }`}
              >
                {recording.status}
              </span>
              {recording.matches && (
                <span className="text-sm font-medium text-purple-600">
                  {recording.matches} matches found
                </span>
              )}
            </div>
            {recording.progress && (
              <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-300"
                  style={{ width: `${recording.progress}%` }}
                ></div>
              </div>
            )}
          </div>
        ))}
      </div>
      <Link href="/recordings">
        <button className="mt-4 w-full py-3 border border-gray-200 dark:border-gray-700 rounded-xl font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
          View All Recordings
        </button>
      </Link>
    </motion.div>
  )
}

function MatchesFeed() {
  const matches = [
    {
      id: 1,
      name: 'Sarah Chen',
      role: 'Investor',
      company: 'Venture Capital Inc',
      score: 92,
      interests: ['AI', 'SaaS', 'Fintech'],
      reason: 'Looking for AI startups in fintech space',
    },
    {
      id: 2,
      name: 'Michael Roberts',
      role: 'Founder',
      company: 'TechStart',
      score: 88,
      interests: ['Marketing', 'Growth', 'SaaS'],
      reason: 'Seeking growth partnerships',
    },
    {
      id: 3,
      name: 'Emily Thompson',
      role: 'Student',
      company: 'MIT',
      score: 85,
      interests: ['ML', 'Research', 'Internship'],
      reason: 'Looking for research collaboration',
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
      className="glass-effect rounded-2xl p-6 shadow-lg"
    >
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
        Top Matches
      </h3>
      <div className="space-y-4">
        {matches.map((match) => (
          <div
            key={match.id}
            className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700 transition-colors cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {match.name}
                </h4>
                <p className="text-sm text-gray-500">
                  {match.role} at {match.company}
                </p>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-purple-600">
                  {match.score}%
                </div>
                <div className="text-xs text-gray-500">match</div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mb-2">
              {match.interests.map((interest) => (
                <span
                  key={interest}
                  className="px-2 py-1 text-xs rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300"
                >
                  {interest}
                </span>
              ))}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {match.reason}
            </p>
            <div className="mt-3 flex gap-2">
              <button className="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors">
                Connect
              </button>
              <button className="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                View
              </button>
            </div>
          </div>
        ))}
      </div>
      <Link href="/matches">
        <button className="mt-4 w-full py-3 border border-gray-200 dark:border-gray-700 rounded-xl font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
          View All Matches
        </button>
      </Link>
    </motion.div>
  )
}
