'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Download, FileText, Clock, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import Image from 'next/image'

interface TranscriptSegment {
  sequence: number
  speaker: string
  text: string
  start_time: number
  end_time: number
  confidence: number
}

interface TranscriptData {
  recording_id: number
  full_text: string
  language: string
  confidence_score: number
  word_count: number
  segments: TranscriptSegment[]
}

interface Recording {
  id: number
  title: string
  status: string
  created_at: string
  duration_seconds?: number
}

export default function TranscriptPage() {
  const params = useParams()
  const recordingId = params.id as string

  const [transcript, setTranscript] = useState<TranscriptData | null>(null)
  const [recording, setRecording] = useState<Recording | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchData()
  }, [recordingId])

  const fetchData = async () => {
    try {
      // Fetch recording details
      const recResponse = await fetch(`http://localhost:8000/api/v1/recordings/${recordingId}`)
      if (!recResponse.ok) throw new Error('Recording not found')
      const recData = await recResponse.json()
      setRecording(recData)

      // Fetch transcript
      const transResponse = await fetch(`http://localhost:8000/api/v1/recordings/${recordingId}/transcript`)
      if (!transResponse.ok) throw new Error('Transcript not found')
      const transData = await transResponse.json()
      setTranscript(transData)

      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Failed to load transcript')
      setLoading(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const downloadTranscript = () => {
    if (!transcript || !recording) return

    const content = transcript.segments
      .map(seg => `[${formatTime(seg.start_time)} - ${formatTime(seg.end_time)}] ${seg.speaker}: ${seg.text}`)
      .join('\n\n')

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${recording.title}_transcript.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading transcript...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Link href="/dashboard">
            <button className="px-6 py-3 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-full hover:shadow-lg transition-shadow">
              Back to Dashboard
            </button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Dashboard</span>
            </Link>
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/lyncsea-logo.png"
                alt="Lyncsea"
                width={100}
                height={100}
                className="rounded-lg"
              />
              <span className="text-3xl font-bold text-gradient tracking-tight">Lyncsea</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Header Card */}
          <div className="glass-effect rounded-2xl p-6 shadow-lg">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {recording?.title}
                </h1>
                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {recording?.duration_seconds && (
                      <span>{Math.floor(recording.duration_seconds / 60)}m {recording.duration_seconds % 60}s</span>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <FileText className="w-4 h-4" />
                    <span>{transcript?.word_count} words</span>
                  </div>
                  <div>
                    Language: {transcript?.language?.toUpperCase()}
                  </div>
                </div>
              </div>
              <button
                onClick={downloadTranscript}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-lg hover:shadow-lg transition-shadow"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>
          </div>

          {/* Full Transcript Card */}
          <div className="glass-effect rounded-2xl p-6 shadow-lg">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Full Transcript
            </h2>
            <div className="prose dark:prose-invert max-w-none">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                {transcript?.full_text}
              </p>
            </div>
          </div>

          {/* Segments Card */}
          <div className="glass-effect rounded-2xl p-6 shadow-lg">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Transcript Segments
            </h2>
            <div className="space-y-4">
              {transcript?.segments.map((segment) => (
                <div
                  key={segment.sequence}
                  className="border-l-4 border-blue-600 pl-4 py-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors rounded-r"
                >
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-xs font-mono text-gray-500">
                      {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
                    </span>
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                      {segment.speaker}
                    </span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">
                    {segment.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}