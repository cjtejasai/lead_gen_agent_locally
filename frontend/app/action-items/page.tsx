'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Calendar, Clock, AlertCircle, CheckCircle2, X, Filter,
  ArrowLeft, User, Building, ExternalLink, Plus
} from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'
import { apiClient } from '@/lib/api'

interface ActionItem {
  id: number
  recording_id: number
  action: string
  deadline: string | null
  deadline_type: string
  priority: 'high' | 'medium' | 'low'
  action_type: string
  quote: string
  speaker_name: string
  contact_email: string
  contact_company: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  created_at: string
  recording_title?: string
}

export default function ActionItemsPage() {
  const [actionItems, setActionItems] = useState<ActionItem[]>([])
  const [filteredItems, setFilteredItems] = useState<ActionItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')
  const [showCalendarModal, setShowCalendarModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState<ActionItem | null>(null)

  useEffect(() => {
    fetchActionItems()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [actionItems, filterStatus, filterPriority])

  const fetchActionItems = async () => {
    try {
      const token = localStorage.getItem('token')
      const data = await apiClient.get('/api/v1/action-items/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setActionItems(data)
    } catch (error) {
      console.error('Error fetching action items:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...actionItems]

    if (filterStatus !== 'all') {
      filtered = filtered.filter(item => item.status === filterStatus)
    }

    if (filterPriority !== 'all') {
      filtered = filtered.filter(item => item.priority === filterPriority)
    }

    // Sort by deadline (soonest first, nulls last)
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
    })

    setFilteredItems(filtered)
  }

  const updateStatus = async (id: number, status: string) => {
    try {
      const token = localStorage.getItem('token')
      await apiClient.patch(`/api/v1/action-items/${id}`,
        { status },
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      fetchActionItems()
    } catch (error) {
      console.error('Error updating status:', error)
    }
  }

  const deleteActionItem = async (id: number) => {
    if (!confirm('Are you sure you want to delete this action item?')) return

    try {
      const token = localStorage.getItem('token')
      await apiClient.delete(`/api/v1/action-items/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      fetchActionItems()
    } catch (error) {
      console.error('Error deleting action item:', error)
    }
  }

  const formatDeadline = (deadline: string | null, deadline_type: string) => {
    if (!deadline) return 'No deadline'

    const date = new Date(deadline)
    const now = new Date()
    const diffTime = date.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Tomorrow'
    if (diffDays < 7) return `In ${diffDays} days`

    return date.toLocaleDateString()
  }

  const getDeadlineColor = (deadline: string | null) => {
    if (!deadline) return 'text-gray-500'

    const date = new Date(deadline)
    const now = new Date()
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return 'text-red-600'
    if (diffDays === 0) return 'text-orange-600'
    if (diffDays <= 3) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-700 border-green-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700'
      case 'in_progress': return 'bg-blue-100 text-blue-700'
      case 'cancelled': return 'bg-gray-100 text-gray-700'
      default: return 'bg-purple-100 text-purple-700'
    }
  }

  const openCalendarModal = (item: ActionItem) => {
    setSelectedItem(item)
    setShowCalendarModal(true)
  }

  const createCalendarEvent = (provider: 'google' | 'outlook' | 'ical') => {
    if (!selectedItem || !selectedItem.deadline) return

    const title = encodeURIComponent(selectedItem.action)
    const details = encodeURIComponent(`${selectedItem.quote}\n\nContact: ${selectedItem.speaker_name}`)
    const start = new Date(selectedItem.deadline).toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'
    const end = new Date(new Date(selectedItem.deadline).getTime() + 60 * 60 * 1000).toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'

    let url = ''

    if (provider === 'google') {
      url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&dates=${start}/${end}`
    } else if (provider === 'outlook') {
      url = `https://outlook.live.com/calendar/0/deeplink/compose?subject=${title}&body=${details}&startdt=${start}&enddt=${end}`
    } else if (provider === 'ical') {
      // Download .ics file
      const ics = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:${start}
DTEND:${end}
SUMMARY:${selectedItem.action}
DESCRIPTION:${selectedItem.quote}
END:VEVENT
END:VCALENDAR`

      const blob = new Blob([ics], { type: 'text/calendar' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = 'event.ics'
      link.click()
      setShowCalendarModal(false)
      return
    }

    window.open(url, '_blank')
    setShowCalendarModal(false)
  }

  const stats = {
    total: actionItems.length,
    pending: actionItems.filter(i => i.status === 'pending').length,
    completed: actionItems.filter(i => i.status === 'completed').length,
    overdue: actionItems.filter(i => i.deadline && new Date(i.deadline) < new Date() && i.status !== 'completed').length
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/" className="flex items-center gap-3">
                <Image src="/lyncsea-logo.png" alt="Lyncsea" width={100} height={100} className="rounded-lg" />
                <span className="text-3xl font-bold text-gradient tracking-tight">Lyncsea</span>
              </Link>
              <span className="text-2xl font-bold text-gray-400">|</span>
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">
                ✅ Action Items
              </span>
            </div>
            <Link href="/dashboard">
              <button className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 transition-colors">
                <ArrowLeft className="w-5 h-5" />
                Dashboard
              </button>
            </Link>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="glass-effect rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Calendar className="w-5 h-5 text-purple-600" />
              </div>
              <span className="text-sm text-gray-600">Total</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">{stats.total}</div>
          </div>

          <div className="glass-effect rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <span className="text-sm text-gray-600">Pending</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">{stats.pending}</div>
          </div>

          <div className="glass-effect rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-600" />
              </div>
              <span className="text-sm text-gray-600">Overdue</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">{stats.overdue}</div>
          </div>

          <div className="glass-effect rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
              <span className="text-sm text-gray-600">Completed</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white">{stats.completed}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="glass-effect rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="font-semibold text-gray-900 dark:text-white">Filters</span>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
            >
              <option value="all">All Priority</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <div className="ml-auto text-sm text-gray-600">
              Showing {filteredItems.length} of {actionItems.length} items
            </div>
          </div>
        </div>

        {/* Action Items List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading action items...</div>
          ) : filteredItems.length === 0 ? (
            <div className="glass-effect rounded-2xl p-12 text-center">
              <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-600">No action items found</p>
            </div>
          ) : (
            filteredItems.map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-effect rounded-2xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{item.action}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full border ${getPriorityColor(item.priority)}`}>
                        {item.priority}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(item.status)}`}>
                        {item.status.replace('_', ' ')}
                      </span>
                    </div>

                    {item.quote && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 italic mb-3 pl-4 border-l-2 border-purple-300">
                        "{item.quote}"
                      </p>
                    )}

                    <div className="flex items-center gap-6 text-sm text-gray-600">
                      {item.deadline && (
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          <span className={getDeadlineColor(item.deadline)}>
                            {formatDeadline(item.deadline, item.deadline_type)}
                          </span>
                        </div>
                      )}

                      {item.speaker_name && (
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          <span>{item.speaker_name}</span>
                        </div>
                      )}

                      {item.contact_company && (
                        <div className="flex items-center gap-2">
                          <Building className="w-4 h-4" />
                          <span>{item.contact_company}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => deleteActionItem(item.id)}
                    className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => updateStatus(item.id, 'in_progress')}
                    disabled={item.status === 'in_progress' || item.status === 'completed'}
                    className="px-4 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Start
                  </button>

                  <button
                    onClick={() => updateStatus(item.id, 'completed')}
                    disabled={item.status === 'completed'}
                    className="px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Complete
                  </button>

                  {item.deadline && (
                    <button
                      onClick={() => openCalendarModal(item)}
                      className="px-4 py-2 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors flex items-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      Add to Calendar
                    </button>
                  )}

                  {item.recording_id && (
                    <Link href={`/transcript/${item.recording_id}`}>
                      <button className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2">
                        <ExternalLink className="w-4 h-4" />
                        View Recording
                      </button>
                    </Link>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Calendar Modal */}
      {showCalendarModal && selectedItem && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCalendarModal(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-white dark:bg-gray-900 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl"
          >
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Add to Calendar</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{selectedItem.action}</p>

            <div className="space-y-3">
              <button
                onClick={() => createCalendarEvent('google')}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <Calendar className="w-5 h-5" />
                Google Calendar
              </button>

              <button
                onClick={() => createCalendarEvent('outlook')}
                className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
              >
                <Calendar className="w-5 h-5" />
                Outlook Calendar
              </button>

              <button
                onClick={() => createCalendarEvent('ical')}
                className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
              >
                <Calendar className="w-5 h-5" />
                Download .ics File
              </button>

              <button
                onClick={() => setShowCalendarModal(false)}
                className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}