'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Upload,
  Sparkles,
  Users,
  TrendingUp,
  Settings,
  Bell,
  Search,
  LogOut,
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { apiClient } from '@/lib/api'

export default function Dashboard() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [user, setUser] = useState<{ full_name: string; email: string } | null>(null)
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          router.push('/login')
          return
        }

        // Fetch user data and stats in parallel
        const [userData, statsData] = await Promise.all([
          apiClient.get('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          apiClient.get('/api/v1/dashboard/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
          })
        ])

        setUser(userData)
        setStats(statsData)
      } catch (error) {
        console.error('Error fetching data:', error)
        router.push('/login')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.replace('/login')
  }

  const getInitials = (name: string) => {
    if (!name || typeof name !== 'string') return 'U'

    // Trim and filter out empty parts
    const parts = name.trim().split(' ').filter(part => part.length > 0)

    if (parts.length >= 2) {
      // First letter of first name + first letter of last name
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    } else if (parts.length === 1 && parts[0].length >= 2) {
      // First two letters of single name
      return parts[0].substring(0, 2).toUpperCase()
    } else if (parts.length === 1 && parts[0].length === 1) {
      // Single letter name
      return parts[0][0].toUpperCase()
    }

    return 'U'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Navigation Header */}
      <nav className="border-b border-gray-200 dark:border-gray-800 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link href="/dashboard" className="flex items-center gap-3">
              <Image
                src="/lyncsea-logo.png"
                alt="Lyncsea"
                width={120}
                height={120}
                className="rounded-lg"
              />
              <span className="text-4xl font-bold text-gradient tracking-tight">Lyncsea</span>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-6 ml-8">
              <Link href="/arya" className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors">
                🎯 Arya
              </Link>
              <Link href="/dhwani" className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors">
                🎙️ Dhwani
              </Link>
              <Link href="/lakshya" className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors">
                💼 Lakshya
              </Link>
              <Link href="/action-items" className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors">
                ✅ Action Items
              </Link>
            </div>

            {/* Search */}
            <div className="flex-1 max-w-xl mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search recordings, matches, interests..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 rounded-full border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors relative">
                <Bell className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-cyan-500 rounded-full"></span>
              </button>

              {/* Profile Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  className="w-10 h-10 rounded-full bg-gradient-to-r from-[#1e3a8a] to-[#0891b2] flex items-center justify-center text-white font-semibold hover:shadow-lg transition-shadow"
                >
                  {user ? getInitials(user.full_name) : 'U'}
                </button>

                {showProfileMenu && (
                  <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
                    <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {user?.full_name || 'User'}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {user?.email || ''}
                      </p>
                    </div>

                    <Link href="/settings">
                      <button className="w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 text-gray-700 dark:text-gray-300">
                        <Settings className="w-4 h-4" />
                        <span className="text-sm">Settings</span>
                      </button>
                    </Link>

                    <button
                      onClick={handleLogout}
                      className="w-full px-4 py-2 text-left hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-3 text-red-600 dark:text-red-400"
                    >
                      <LogOut className="w-4 h-4" />
                      <span className="text-sm">Logout</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        {loading ? (
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="glass-effect rounded-2xl p-6 shadow-lg animate-pulse">
                <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={<Upload className="w-6 h-6" />}
              label="Total Recordings"
              value={stats?.recordings?.total?.toString() || "0"}
              change={stats?.recordings?.change || "No activity"}
              positive={stats?.recordings?.this_week > 0}
            />
            <StatCard
              icon={<Users className="w-6 h-6" />}
              label="Active Leads"
              value={stats?.leads?.total?.toString() || "0"}
              change={stats?.leads?.change || "No new leads"}
              positive={stats?.leads?.this_week > 0}
            />
            <StatCard
              icon={<Sparkles className="w-6 h-6" />}
              label="Events Found"
              value={stats?.events?.total?.toString() || "0"}
              change={stats?.events?.change || "No events"}
              positive={stats?.events?.this_week > 0}
            />
            <StatCard
              icon={<TrendingUp className="w-6 h-6" />}
              label="Connections Made"
              value={stats?.connections?.total?.toString() || "0"}
              change={stats?.connections?.change || "No connections"}
              positive={stats?.connections?.this_week > 0}
            />
          </div>
        )}

        {/* Agent Cards Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
            🤖 Your AI Agent Team
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <AgentCard
              name="Arya"
              icon="🎯"
              role="Event Scout"
              description="Discover networking events matching your interests"
              href="/arya"
              gradient="from-blue-500 to-cyan-500"
              stat="12 events found"
            />
            <AgentCard
              name="Dhwani"
              icon="🎙️"
              role="Voice Intelligence"
              description="Record and transcribe conversations with AI"
              href="/dhwani"
              gradient="from-purple-500 to-pink-500"
              stat="5 recordings"
            />
            <AgentCard
              name="Lakshya"
              icon="💼"
              role="Lead Generator"
              description="Extract leads and opportunities automatically"
              href="/lakshya"
              gradient="from-orange-500 to-red-500"
              stat="24 leads generated"
            />
          </div>
        </motion.div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Recent Recordings */}
          <div className="lg:col-span-2 space-y-6">
            <RecentRecordings />
          </div>

          {/* Right Column - Recent Activity & Action Items */}
          <div className="space-y-6">
            <UpcomingActionItems />
            <RecentActivity />
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
        <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl text-blue-600">
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
  const [recordings, setRecordings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecordings = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        const data = await apiClient.get('/api/v1/recordings/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        setRecordings(data.slice(0, 3)) // Only show 3 most recent
      } catch (error) {
        console.error('Error fetching recordings:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRecordings()
  }, [])

  if (loading) {
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
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </motion.div>
    )
  }

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
            className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors cursor-pointer"
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
                <span className="text-sm font-medium text-blue-600">
                  {recording.matches} matches found
                </span>
              )}
            </div>
            {recording.progress && (
              <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-900 to-cyan-600 transition-all duration-300"
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

function AgentCard({
  name,
  icon,
  role,
  description,
  href,
  gradient,
  stat,
}: {
  name: string
  icon: string
  role: string
  description: string
  href: string
  gradient: string
  stat: string
}) {
  return (
    <Link href={href}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -4, scale: 1.02 }}
        className="glass-effect rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer border-2 border-transparent hover:border-blue-200 dark:hover:border-blue-800"
      >
        <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${gradient} text-white mb-4 shadow-lg text-3xl`}>
          {icon}
        </div>
        <h3 className="text-xl font-bold mb-1 text-gray-900 dark:text-white">
          {name}
        </h3>
        <p className={`text-sm font-semibold mb-3 bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
          {role}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
          {description}
        </p>
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            {stat}
          </span>
          <span className="text-blue-600 dark:text-blue-400 text-sm font-medium">
            Open →
          </span>
        </div>
      </motion.div>
    </Link>
  )
}

function UpcomingActionItems() {
  const [actionItems, setActionItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchActionItems = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        const data = await apiClient.get('/api/v1/action-items/?status=pending', {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        // Sort by deadline and take top 5
        const sorted = data
          .filter((item: any) => item.deadline) // Only items with deadlines
          .sort((a: any, b: any) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime())
          .slice(0, 5)

        setActionItems(sorted)
      } catch (error) {
        console.error('Error fetching action items:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchActionItems()
  }, [])

  const formatDeadline = (deadline: string) => {
    const date = new Date(deadline)
    const now = new Date()
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return 'Overdue'
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Tomorrow'
    if (diffDays < 7) return `${diffDays} days`
    return date.toLocaleDateString()
  }

  const getDeadlineColor = (deadline: string) => {
    const date = new Date(deadline)
    const now = new Date()
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return 'text-red-600'
    if (diffDays === 0) return 'text-orange-600'
    if (diffDays <= 3) return 'text-yellow-600'
    return 'text-green-600'
  }

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.25 }}
        className="glass-effect rounded-2xl p-6 shadow-lg"
      >
        <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-purple-600" />
          Upcoming Actions
        </h3>
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.25 }}
      className="glass-effect rounded-2xl p-6 shadow-lg"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-purple-600" />
          Upcoming Actions
        </h3>
        <Link href="/action-items">
          <span className="text-sm text-blue-600 dark:text-blue-400 hover:underline cursor-pointer">
            View all →
          </span>
        </Link>
      </div>

      {actionItems.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No upcoming actions</p>
        </div>
      ) : (
        <div className="space-y-3">
          {actionItems.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700 transition-colors"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                  {item.action}
                </p>
                {item.priority === 'high' && (
                  <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                )}
              </div>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span className={getDeadlineColor(item.deadline)}>
                    {formatDeadline(item.deadline)}
                  </span>
                </div>
                {item.speaker_name && (
                  <span className="text-gray-500 truncate max-w-[100px]">
                    {item.speaker_name}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}

function RecentActivity() {
  const activities = [
    {
      id: 1,
      agent: 'Dhwani',
      icon: '🎙️',
      action: 'Processed recording',
      target: 'Tech Conference 2024',
      time: '2 hours ago',
      color: 'text-purple-600',
    },
    {
      id: 2,
      agent: 'Lakshya',
      icon: '💼',
      action: 'Found 3 new leads',
      target: 'from latest recording',
      time: '3 hours ago',
      color: 'text-orange-600',
    },
    {
      id: 3,
      agent: 'Arya',
      icon: '🎯',
      action: 'Discovered 2 events',
      target: 'matching your interests',
      time: '5 hours ago',
      color: 'text-blue-600',
    },
    {
      id: 4,
      agent: 'Dhwani',
      icon: '🎙️',
      action: 'Completed transcription',
      target: 'Investor Meeting',
      time: '1 day ago',
      color: 'text-purple-600',
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
        Recent Activity
      </h3>
      <div className="space-y-4">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div className="text-2xl flex-shrink-0">{activity.icon}</div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                <span className={activity.color}>{activity.agent}</span> {activity.action}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                {activity.target}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                {activity.time}
              </p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
