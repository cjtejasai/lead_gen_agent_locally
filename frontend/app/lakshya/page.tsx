'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { motion } from 'framer-motion'
import {
  Users, Building2, Briefcase, Mail, Linkedin, Globe,
  ArrowLeft, Filter, CheckCircle, Clock, XCircle, Tag
} from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Lead {
  id: number
  recording_id: number
  name: string
  company: string | null
  role: string | null
  opportunity_type: string | null
  opportunity_description: string | null
  priority: string | null
  linkedin_url: string | null
  email: string | null
  company_website: string | null
  notes: string | null
  status: string
  created_at: string
  updated_at: string
}

export default function LakshyaPage() {
  const router = useRouter()
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    fetchLeads()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchLeads = async () => {
    try {
      const token = localStorage.getItem('token')
      const data = await apiClient.get('/api/v1/leads/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setLeads(data)
    } catch (err: any) {
      if (err.message?.includes('401')) {
        router.push('/login')
      } else {
        setError('Error loading leads')
      }
    } finally {
      setLoading(false)
    }
  }

  const updateLeadStatus = async (leadId: number, newStatus: string) => {
    try {
      const token = localStorage.getItem('token')
      await apiClient.patch(`/api/v1/leads/${leadId}/status?status=${newStatus}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setLeads(leads.map(lead =>
        lead.id === leadId ? { ...lead, status: newStatus } : lead
      ))
    } catch (err) {
      console.error('Error updating lead status:', err)
    }
  }

  const deleteLead = async (leadId: number) => {
    if (!confirm('Are you sure you want to delete this lead?')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      await apiClient.delete(`/api/v1/leads/${leadId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setLeads(leads.filter(lead => lead.id !== leadId))
    } catch (err) {
      console.error('Error deleting lead:', err)
    }
  }

  const getPriorityColor = (priority: string | null) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'low':
        return 'bg-green-100 text-green-700 border-green-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'contacted':
        return <Mail className="w-4 h-4" />
      case 'in_progress':
        return <Clock className="w-4 h-4" />
      case 'closed':
        return <CheckCircle className="w-4 h-4" />
      default:
        return <Tag className="w-4 h-4" />
    }
  }

  const filteredLeads = leads.filter(lead => {
    const statusMatch = filterStatus === 'all' || lead.status === filterStatus
    const priorityMatch = filterPriority === 'all' || lead.priority?.toLowerCase() === filterPriority
    return statusMatch && priorityMatch
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading leads...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-blue-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-6">
              <Link href="/dashboard" className="flex items-center gap-3">
                <Image
                  src="/lyncsea-logo.png"
                  alt="Lyncsea"
                  width={100}
                  height={100}
                  className="rounded-lg"
                />
                <span className="text-3xl font-bold text-gradient tracking-tight">Lyncsea</span>
              </Link>
              <span className="text-2xl font-bold text-gray-400">|</span>
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">
                🎯 Lakshya - Lead Hunter
              </span>
            </div>

            <nav className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-blue-600 transition-colors flex items-center gap-3"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Lead Database
          </h1>
          <p className="text-gray-600">
            AI-extracted business opportunities from your conversations
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8 flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="in_progress">In Progress</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Priority:</span>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div className="ml-auto text-sm text-gray-600">
            {filteredLeads.length} lead{filteredLeads.length !== 1 ? 's' : ''} found
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600">
            {error}
          </div>
        )}

        {/* Leads Grid */}
        {filteredLeads.length === 0 ? (
          <div className="text-center py-16">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No leads found
            </h3>
            <p className="text-gray-500 mb-6">
              Generate leads from your conversation recordings to start building your network
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredLeads.map((lead, index) => (
              <motion.div
                key={lead.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="p-6">
                  {/* Priority Badge */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${getPriorityColor(lead.priority)}`}>
                      {lead.priority?.toUpperCase() || 'MEDIUM'} PRIORITY
                    </div>
                    <button
                      onClick={() => deleteLead(lead.id)}
                      className="text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Name & Company */}
                  <h3 className="text-lg font-bold text-gray-900 mb-1">
                    {lead.name}
                  </h3>
                  {lead.role && (
                    <p className="text-sm text-gray-600 mb-2">{lead.role}</p>
                  )}
                  {lead.company && (
                    <div className="flex items-center gap-2 text-sm text-gray-700 mb-4">
                      <Building2 className="w-4 h-4" />
                      {lead.company}
                    </div>
                  )}

                  {/* Opportunity */}
                  {lead.opportunity_description && (
                    <div className="mb-4 p-3 bg-purple-50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Briefcase className="w-4 h-4 text-purple-600" />
                        <p className="text-xs text-purple-700 font-semibold">
                          {lead.opportunity_type || 'Opportunity'}
                        </p>
                      </div>
                      <p className="text-xs text-purple-600 line-clamp-2">
                        {lead.opportunity_description}
                      </p>
                    </div>
                  )}

                  {/* Contact Links */}
                  <div className="flex gap-2 mb-4">
                    {lead.linkedin_url && (
                      <a
                        href={lead.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-xs"
                      >
                        <Linkedin className="w-3 h-3" />
                        LinkedIn
                      </a>
                    )}
                    {lead.email && (
                      <a
                        href={`mailto:${lead.email}`}
                        className="flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-xs"
                      >
                        <Mail className="w-3 h-3" />
                        Email
                      </a>
                    )}
                    {lead.company_website && (
                      <a
                        href={lead.company_website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-xs"
                      >
                        <Globe className="w-3 h-3" />
                        Website
                      </a>
                    )}
                  </div>

                  {/* Status Selector */}
                  <div className="flex items-center gap-2">
                    {getStatusIcon(lead.status)}
                    <select
                      value={lead.status}
                      onChange={(e) => updateLeadStatus(lead.id, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="in_progress">In Progress</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}