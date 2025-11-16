'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Mic, Upload as UploadIcon, Bluetooth, ChevronDown, Play, Pause, Square,
  Check, Loader2, FileAudio, Calendar, MapPin, Camera, X, ArrowLeft, FileText, Clock
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { apiClient, API_URL } from '@/lib/api'

type RecordingStatus = 'idle' | 'recording' | 'paused' | 'stopped' | 'uploading' | 'diarizing' | 'transcribing' | 'generating_leads' | 'complete'
type ActiveTab = 'record' | 'upload'

interface AudioDevice {
  deviceId: string
  label: string
  kind: string
}

interface Recording {
  id: number
  title: string
  filename: string  // Add filename field
  status: string
  duration: number | null
  created_at: string
  event_name?: string
}

export default function DhwaniPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<ActiveTab>('record')
  const [status, setStatus] = useState<RecordingStatus>('idle')
  const [devices, setDevices] = useState<AudioDevice[]>([])
  const [selectedDevice, setSelectedDevice] = useState<string>('')
  const [showDeviceMenu, setShowDeviceMenu] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [recordings, setRecordings] = useState<Recording[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalRecordings, setTotalRecordings] = useState(0)
  const recordingsPerPage = 10

  // Event details
  const [eventName, setEventName] = useState('')
  const [eventDate, setEventDate] = useState('')
  const [eventLocation, setEventLocation] = useState('')
  const [visitingCards, setVisitingCards] = useState<File[]>([])

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cardInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadDevices()
    fetchRecordings()
  }, [])

  // Clear audioBlob when switching tabs to prevent wrong file upload
  useEffect(() => {
    console.log('Tab changed to:', activeTab, '- Clearing audioBlob and resetting status')
    setAudioBlob(null)
    setStatus('idle')
    setRecordingTime(0)
  }, [activeTab])

  const loadDevices = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
      const deviceList = await navigator.mediaDevices.enumerateDevices()
      const audioInputs = deviceList
        .filter(device => device.kind === 'audioinput')
        .map(device => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.slice(0, 5)}`,
          kind: device.kind,
        }))

      setDevices(audioInputs)
      if (audioInputs.length > 0) {
        setSelectedDevice(audioInputs[0].deviceId)
      }
    } catch (error) {
      console.error('Error loading audio devices:', error)
    }
  }

  const fetchRecordings = async () => {
    try {
      const token = localStorage.getItem('token')
      const data = await apiClient.get('/api/v1/recordings/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setRecordings(data)
    } catch (error) {
      console.error('Error fetching recordings:', error)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: selectedDevice ? { exact: selectedDevice } : undefined,
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      })

      // FIX 1: Add mimeType fallback for Safari/iOS compatibility
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : 'audio/mp4'  // Safari/iOS fallback

      console.log('Using mimeType:', mimeType)

      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      // FIX 2: Add debug logging to track chunk sizes
      mediaRecorder.ondataavailable = (event) => {
        console.log('Audio chunk received:', event.data.size, 'bytes')
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        } else {
          console.warn('Received empty audio chunk')
        }
      }

      mediaRecorder.onstop = () => {
        const totalSize = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0)
        console.log('Recording stopped - Total chunks:', audioChunksRef.current.length, 'Total size:', totalSize, 'bytes')

        if (totalSize === 0) {
          console.error('No audio data captured!')
          alert('Recording failed: No audio data captured. Please check microphone permissions.')
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType })
        setAudioBlob(audioBlob)

        // FIX 3: Delay track stop to ensure buffer is fully flushed
        setTimeout(() => {
          stream.getTracks().forEach(track => track.stop())
          console.log('Audio tracks stopped')
        }, 200)
      }

      // FIX 4: Use 250ms timeslice for reliable chunk collection
      // Flushes 4 times per second - prevents buffer overflow and dropped frames
      mediaRecorder.start(250)
      setStatus('recording')
      timerRef.current = setInterval(() => setRecordingTime(prev => prev + 1), 1000)
      console.log('Recording started with mimeType:', mimeType, '(250ms chunks)')
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Failed to start recording. Please check microphone permissions.')
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause()
      setStatus('paused')
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume()
      setStatus('recording')
      timerRef.current = setInterval(() => setRecordingTime(prev => prev + 1), 1000)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      setStatus('stopped')
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    console.log('handleFileUpload called - file from input:', file?.name, file?.type, file?.size)
    if (file && file.type.includes('audio')) {
      console.log('Setting audioBlob to:', file.name, file.type, file.size)
      setAudioBlob(file)
      setStatus('stopped')
    } else {
      console.log('Invalid file type or no file selected')
      alert('Please upload a valid audio file (.wav, .mp3, etc.)')
    }
  }

  const handleCardUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setVisitingCards(prev => [...prev, ...files])
  }

  const removeCard = (index: number) => {
    setVisitingCards(prev => prev.filter((_, i) => i !== index))
  }

  const uploadRecording = async () => {
    if (!audioBlob) return

    // Validate mandatory event fields
    if (!eventName || !eventDate) {
      alert('Please fill in Event Name and Event Date before uploading')
      return
    }

    console.log('uploadRecording called - audioBlob details:')
    console.log('  - Type:', audioBlob.type)
    console.log('  - Size:', audioBlob.size)
    console.log('  - ActiveTab:', activeTab)
    console.log('  - Event Name:', eventName)
    console.log('  - Event Date:', eventDate)
    console.log('  - Event Location:', eventLocation)
    console.log('  - Is File instance?', audioBlob instanceof File)
    if (audioBlob instanceof File) {
      console.log('  - File name:', (audioBlob as File).name)
    }

    setStatus('uploading')

    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const filename = activeTab === 'record' ? `recording_${timestamp}.webm` : `upload_${timestamp}.${audioBlob.type.split('/')[1]}`

      console.log('Generated filename:', filename)
      console.log('Appending to FormData with filename:', filename)

      formData.append('file', audioBlob, filename)
      formData.append('title', eventName || `Recording ${new Date().toLocaleString()}`)
      if (eventDate) formData.append('event_date', eventDate)
      if (eventLocation) formData.append('event_location', eventLocation)

      visitingCards.forEach((card, index) => {
        formData.append(`visiting_card_${index}`, card)
      })

      const response = await fetch(`${API_URL}/api/v1/recordings/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      })

      if (!response.ok) throw new Error('Upload failed')

      const data = await response.json()
      const recordingId = data.recording_id

      // Start processing
      const processResponse = await fetch(`${API_URL}/api/v1/recordings/${recordingId}/process`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!processResponse.ok) {
        throw new Error('Processing failed')
      }

      // Poll for status updates
      const pollStatus = async () => {
        const statusResponse = await fetch(`${API_URL}/api/v1/recordings/${recordingId}/status`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!statusResponse.ok) return

        const statusData = await statusResponse.json()
        console.log('Status poll:', statusData)

        // Map backend status to UI state
        switch (statusData.status) {
          case 'pending':
            setStatus('uploading')
            break
          case 'processing':
            // Alternate between diarizing and transcribing for visual effect
            setStatus(prev => prev === 'diarizing' ? 'transcribing' : 'diarizing')
            break
          case 'analyzing':
            setStatus('generating_leads')
            break
          case 'completed':
            setStatus('complete')
            fetchRecordings()

            // Clean up after showing completion
            setTimeout(() => {
              setStatus('idle')
              setAudioBlob(null)
              setRecordingTime(0)
              setEventName('')
              setEventDate('')
              setEventLocation('')
              setVisitingCards([])
            }, 2000)

            return true // Stop polling
          case 'failed':
            setStatus('stopped')
            alert('Processing failed')
            return true // Stop polling
        }

        return false // Continue polling
      }

      // Poll every 2 seconds until complete
      const pollInterval = setInterval(async () => {
        const done = await pollStatus()
        if (done) clearInterval(pollInterval)
      }, 2000)

      // Initial poll
      await pollStatus()

    } catch (error) {
      console.error('Upload error:', error)
      alert('Failed to upload recording')
      setStatus('stopped')
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const deleteRecording = async (id: number) => {
    if (!confirm('Are you sure you want to delete this recording?')) return

    try {
      const token = localStorage.getItem('token')
      await apiClient.delete(`/api/v1/recordings/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      fetchRecordings() // Refresh the list
    } catch (error) {
      console.error('Error deleting recording:', error)
      alert('Failed to delete recording')
    }
  }

  const playRecording = async (id: number) => {
    try {
      const token = localStorage.getItem('token')
      const data = await apiClient.get(`/api/v1/recordings/${id}/play`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      // Open audio in new tab or play inline
      if (data.playback_url) {
        window.open(data.playback_url, '_blank')
      }
    } catch (error) {
      console.error('Error playing recording:', error)
      alert('Failed to load audio playback')
    }
  }

  // Pagination
  const totalPages = Math.ceil(recordings.length / recordingsPerPage)
  const paginatedRecordings = recordings.slice(
    (currentPage - 1) * recordingsPerPage,
    currentPage * recordingsPerPage
  )

  const selectedDeviceLabel = devices.find(d => d.deviceId === selectedDevice)?.label || 'Select Device'

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
                🎙️ Dhwani - Voice Studio
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
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Event Details & Recording */}
          <div className="lg:col-span-2 space-y-6">
            {/* Event Details Card */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-effect rounded-2xl p-6 shadow-lg">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-600" />
                Event Details
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                <input
                  type="text"
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  placeholder="Event Name"
                  className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <input
                  type="date"
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                  className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <input
                  type="text"
                  value={eventLocation}
                  onChange={(e) => setEventLocation(e.target.value)}
                  placeholder="Location"
                  className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <div>
                  <input
                    type="file"
                    ref={cardInputRef}
                    onChange={handleCardUpload}
                    accept="image/*"
                    multiple
                    className="hidden"
                  />
                  <button
                    onClick={() => cardInputRef.current?.click()}
                    className="w-full px-4 py-2 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg hover:border-purple-400 transition-colors flex items-center justify-center gap-2"
                  >
                    <Camera className="w-4 h-4" />
                    <span className="text-sm">Visiting Cards ({visitingCards.length})</span>
                  </button>
                </div>
              </div>
              {visitingCards.length > 0 && (
                <div className="mt-4 flex gap-2 flex-wrap">
                  {visitingCards.map((card, index) => (
                    <div key={index} className="relative group w-16 h-16">
                      <img src={URL.createObjectURL(card)} alt={`Card ${index + 1}`} className="w-full h-full object-cover rounded-lg" />
                      <button
                        onClick={() => removeCard(index)}
                        className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>

            {/* Record/Upload Card */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-effect rounded-2xl p-6 shadow-lg">
              {/* Tabs */}
              <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setActiveTab('record')}
                  className={`pb-3 px-4 font-semibold transition-colors relative ${
                    activeTab === 'record' ? 'text-purple-600' : 'text-gray-500'
                  }`}
                >
                  <Mic className="w-4 h-4 inline mr-2" />
                  Record
                  {activeTab === 'record' && <motion.div layoutId="tab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-600" />}
                </button>
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`pb-3 px-4 font-semibold transition-colors relative ${
                    activeTab === 'upload' ? 'text-purple-600' : 'text-gray-500'
                  }`}
                >
                  <UploadIcon className="w-4 h-4 inline mr-2" />
                  Upload
                  {activeTab === 'upload' && <motion.div layoutId="tab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-600" />}
                </button>
              </div>

              <AnimatePresence mode="wait">
                {activeTab === 'record' && (
                  <motion.div key="record" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    {/* Device Selection */}
                    <div className="mb-4">
                      <div className="relative">
                        <button
                          onClick={() => setShowDeviceMenu(!showDeviceMenu)}
                          disabled={status === 'recording' || status === 'paused'}
                          className="w-full flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 transition-colors disabled:opacity-50"
                        >
                          <div className="flex items-center gap-2">
                            <Bluetooth className="w-4 h-4 text-purple-600" />
                            <span className="text-sm">{selectedDeviceLabel}</span>
                          </div>
                          <ChevronDown className={`w-4 h-4 transition-transform ${showDeviceMenu ? 'rotate-180' : ''}`} />
                        </button>
                        {showDeviceMenu && (
                          <div className="absolute z-10 w-full mt-2 bg-white dark:bg-gray-800 border rounded-lg shadow-lg">
                            {devices.map((device) => (
                              <button
                                key={device.deviceId}
                                onClick={() => {
                                  setSelectedDevice(device.deviceId)
                                  setShowDeviceMenu(false)
                                }}
                                className="w-full text-left px-4 py-2 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors flex items-center justify-between"
                              >
                                <span className="text-sm">{device.label}</span>
                                {selectedDevice === device.deviceId && <Check className="w-4 h-4 text-purple-600" />}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Recording Visualizer */}
                    <div className="mb-4 h-32 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl flex items-center justify-center">
                      {(status === 'recording' || status === 'paused' || status === 'stopped') ? (
                        <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                          {formatTime(recordingTime)}
                        </div>
                      ) : (
                        <Mic className="w-12 h-12 text-purple-400" />
                      )}
                    </div>

                    {/* Controls */}
                    <div className="flex items-center justify-center gap-3">
                      {status === 'idle' && (
                        <button onClick={startRecording} className="w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg">
                          <Mic className="w-8 h-8 text-white" />
                        </button>
                      )}
                      {status === 'recording' && (
                        <>
                          <button onClick={pauseRecording} className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center">
                            <Pause className="w-6 h-6 text-white" />
                          </button>
                          <button onClick={stopRecording} className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
                            <Square className="w-6 h-6 text-white" />
                          </button>
                        </>
                      )}
                      {status === 'paused' && (
                        <>
                          <button onClick={resumeRecording} className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                            <Play className="w-6 h-6 text-white" />
                          </button>
                          <button onClick={stopRecording} className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
                            <Square className="w-6 h-6 text-white" />
                          </button>
                        </>
                      )}
                    </div>
                  </motion.div>
                )}

                {activeTab === 'upload' && (
                  <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="audio/*,.wav,.mp3,.m4a" className="hidden" />
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-12 text-center hover:border-purple-400 transition-colors cursor-pointer"
                    >
                      {!audioBlob ? (
                        <>
                          <FileAudio className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                          <p className="text-sm text-gray-600">Click to upload audio file</p>
                          <p className="text-xs text-gray-500 mt-2">WAV, MP3, M4A</p>
                        </>
                      ) : (
                        <>
                          <Check className="w-16 h-16 mx-auto mb-4 text-green-600" />
                          <p className="text-sm text-gray-900 dark:text-white font-medium">File uploaded!</p>
                        </>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Upload Button */}
              {(status === 'stopped' || (activeTab === 'upload' && audioBlob)) && (
                <button
                  onClick={uploadRecording}
                  disabled={status !== 'stopped'}
                  className="w-full mt-6 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <UploadIcon className="w-5 h-5" />
                  Upload & Process
                </button>
              )}
            </motion.div>

            {/* Recordings List */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-effect rounded-2xl p-6 shadow-lg">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-purple-600" />
                Recordings ({recordings.length})
              </h2>
              <div className="space-y-3">
                {recordings.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No recordings yet</p>
                ) : (
                  <>
                    {paginatedRecordings.map((recording) => (
                      <div key={recording.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white">{recording.title}</h3>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-mono">{recording.filename}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              recording.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                            }`}>
                              {recording.status}
                            </span>
                            <button
                              onClick={() => deleteRecording(recording.id)}
                              className="p-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                              title="Delete recording"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {formatDuration(recording.duration)}
                            </span>
                            <span>{new Date(recording.created_at).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => playRecording(recording.id)}
                              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors flex items-center gap-1"
                            >
                              <Play className="w-3 h-3" />
                              Play Audio
                            </button>
                            {recording.status === 'completed' && (
                              <Link href={`/transcript/${recording.id}`}>
                                <button className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors flex items-center gap-1">
                                  <FileText className="w-3 h-3" />
                                  View Transcript
                                </button>
                              </Link>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Pagination Controls */}
                    {totalPages > 1 && (
                      <div className="flex items-center justify-center gap-2 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={currentPage === 1}
                          className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Previous
                        </button>
                        <div className="flex items-center gap-1">
                          {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                            <button
                              key={page}
                              onClick={() => setCurrentPage(page)}
                              className={`px-3 py-1 text-sm rounded transition-colors ${
                                currentPage === page
                                  ? 'bg-purple-600 text-white'
                                  : 'text-gray-600 dark:text-gray-400 hover:bg-purple-50 dark:hover:bg-purple-900/20'
                              }`}
                            >
                              {page}
                            </button>
                          ))}
                        </div>
                        <button
                          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                          disabled={currentPage === totalPages}
                          className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Next
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </motion.div>
          </div>

          {/* Right Column - Processing Status */}
          <div className="space-y-6">
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-effect rounded-2xl p-6 shadow-lg sticky top-24">
              <h2 className="text-xl font-bold mb-6 text-gray-900 dark:text-white">Processing Status</h2>
              <div className="space-y-4">
                {/* Upload */}
                <div className={`flex items-center gap-3 ${['uploading', 'diarizing', 'transcribing', 'generating_leads', 'complete'].includes(status) ? 'text-green-600' : 'text-gray-400'}`}>
                  {status === 'uploading' ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                  <span className="font-medium">Upload Audio</span>
                </div>

                {/* Diarization */}
                <div className={`flex items-center gap-3 ${['diarizing', 'transcribing', 'generating_leads', 'complete'].includes(status) ? 'text-purple-600' : 'text-gray-400'}`}>
                  {status === 'diarizing' ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                  <div>
                    <p className="font-medium">Speaker Diarization</p>
                    {status === 'diarizing' && <p className="text-xs text-gray-600">Identifying speakers...</p>}
                  </div>
                </div>

                {/* Transcription */}
                <div className={`flex items-center gap-3 ${['transcribing', 'generating_leads', 'complete'].includes(status) ? 'text-purple-600' : 'text-gray-400'}`}>
                  {status === 'transcribing' ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                  <div>
                    <p className="font-medium">Transcription</p>
                    {status === 'transcribing' && <p className="text-xs text-gray-600">Converting speech to text...</p>}
                  </div>
                </div>

                {/* Lead Generation */}
                <div className={`flex items-center gap-3 ${['generating_leads', 'complete'].includes(status) ? 'text-orange-600' : 'text-gray-400'}`}>
                  {status === 'generating_leads' ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                  <div>
                    <p className="font-medium">Lead Generation</p>
                    {status === 'generating_leads' && <p className="text-xs text-gray-600">Lakshya is finding opportunities...</p>}
                  </div>
                </div>

                {status === 'complete' && (
                  <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <p className="text-green-700 dark:text-green-300 font-medium">✨ All done! Check your recordings below.</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}