'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Mic,
  MicOff,
  Bluetooth,
  ChevronDown,
  Upload,
  Sparkles,
  Play,
  Pause,
  Square,
  Check,
  Loader2,
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

type RecordingStatus = 'idle' | 'recording' | 'paused' | 'stopped' | 'uploading' | 'processing'

interface AudioDevice {
  deviceId: string
  label: string
  kind: string
}

export default function RecordPage() {
  const router = useRouter()
  const [status, setStatus] = useState<RecordingStatus>('idle')
  const [devices, setDevices] = useState<AudioDevice[]>([])
  const [selectedDevice, setSelectedDevice] = useState<string>('')
  const [showDeviceMenu, setShowDeviceMenu] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  // Load available audio devices
  useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    try {
      // Request permission first
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

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        setAudioBlob(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start(1000) // Collect data every second
      setStatus('recording')

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Failed to start recording. Please check microphone permissions.')
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause()
      setStatus('paused')
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume()
      setStatus('recording')

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      setStatus('stopped')
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const uploadRecording = async () => {
    if (!audioBlob) return

    setStatus('uploading')

    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const filename = `recording_${timestamp}.webm`
      formData.append('file', audioBlob, filename)
      formData.append('title', `Recording ${new Date().toLocaleString()}`)

      // Upload to backend with auth token
      const response = await fetch('http://localhost:8000/api/v1/recordings/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      console.log('Upload successful:', data)

      setStatus('processing')
      setUploadProgress(100)

      // Redirect to dashboard after a delay
      setTimeout(() => {
        router.push('/dashboard')
      }, 2000)

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

  const selectedDeviceLabel = devices.find(d => d.deviceId === selectedDevice)?.label || 'Select Device'

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 glass-effect sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/lyncsea-logo.png"
                alt="Lyncsea"
                width={120}
                height={120}
                className="rounded-lg"
              />
              <span className="text-4xl font-bold text-gradient tracking-tight">Lyncsea</span>
            </Link>
            <Link href="/dashboard">
              <button className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 transition-colors">
                Back to Dashboard
              </button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-effect rounded-3xl p-8 md:p-12 shadow-2xl"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4 text-gradient">
              Audio Recording
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Record conversations and let AI extract valuable insights
            </p>
          </div>

          {/* Device Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Audio Input Device
            </label>
            <div className="relative">
              <button
                onClick={() => setShowDeviceMenu(!showDeviceMenu)}
                disabled={status === 'recording' || status === 'paused'}
                className="w-full flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-blue-300 dark:hover:border-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-3">
                  <Bluetooth className="w-5 h-5 text-blue-600" />
                  <span className="text-gray-900 dark:text-white">{selectedDeviceLabel}</span>
                </div>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${showDeviceMenu ? 'rotate-180' : ''}`} />
              </button>

              <AnimatePresence>
                {showDeviceMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute z-10 w-full mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg overflow-hidden"
                  >
                    {devices.map((device) => (
                      <button
                        key={device.deviceId}
                        onClick={() => {
                          setSelectedDevice(device.deviceId)
                          setShowDeviceMenu(false)
                        }}
                        className="w-full text-left px-4 py-3 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors flex items-center justify-between"
                      >
                        <span className="text-gray-900 dark:text-white">{device.label}</span>
                        {selectedDevice === device.deviceId && (
                          <Check className="w-5 h-5 text-blue-600" />
                        )}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Recording Visualizer */}
          <div className="mb-8">
            <div className="relative h-48 bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-2xl flex items-center justify-center overflow-hidden">
              {/* Animated waves when recording */}
              {(status === 'recording' || status === 'paused') && (
                <div className="absolute inset-0 flex items-center justify-center">
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 bg-gradient-to-t from-blue-900 to-cyan-600 rounded-full"
                      animate={{
                        height: status === 'recording' ? [20, 100, 20] : 20,
                      }}
                      transition={{
                        duration: 0.8,
                        repeat: Infinity,
                        delay: i * 0.1,
                      }}
                      style={{ left: `${20 + i * 15}%` }}
                    />
                  ))}
                </div>
              )}

              {/* Center Icon/Timer */}
              <div className="relative z-10 text-center">
                {status === 'idle' && (
                  <Mic className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                )}
                {(status === 'recording' || status === 'paused' || status === 'stopped') && (
                  <div className="text-5xl font-bold text-gradient mb-2">
                    {formatTime(recordingTime)}
                  </div>
                )}
                {status === 'uploading' && (
                  <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto" />
                )}
                {status === 'processing' && (
                  <Check className="w-16 h-16 text-green-600 mx-auto" />
                )}
              </div>
            </div>
          </div>

          {/* Recording Controls */}
          <div className="flex items-center justify-center gap-4 mb-8">
            {status === 'idle' && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={startRecording}
                className="w-20 h-20 bg-gradient-to-r from-blue-900 to-cyan-600 rounded-full flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow"
              >
                <Mic className="w-10 h-10 text-white" />
              </motion.button>
            )}

            {status === 'recording' && (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={pauseRecording}
                  className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center shadow-lg"
                >
                  <Pause className="w-8 h-8 text-white" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={stopRecording}
                  className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center shadow-lg"
                >
                  <Square className="w-8 h-8 text-white" />
                </motion.button>
              </>
            )}

            {status === 'paused' && (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={resumeRecording}
                  className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center shadow-lg"
                >
                  <Play className="w-8 h-8 text-white" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={stopRecording}
                  className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center shadow-lg"
                >
                  <Square className="w-8 h-8 text-white" />
                </motion.button>
              </>
            )}

            {status === 'stopped' && audioBlob && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={uploadRecording}
                className="px-8 py-4 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-full font-semibold flex items-center gap-3 shadow-lg"
              >
                <Upload className="w-5 h-5" />
                Upload & Process
              </motion.button>
            )}
          </div>

          {/* Status Message */}
          <div className="text-center">
            {status === 'idle' && (
              <p className="text-gray-600 dark:text-gray-400">
                Select an audio device and click the microphone to start recording
              </p>
            )}
            {status === 'recording' && (
              <p className="text-blue-600 font-medium animate-pulse">
                Recording in progress...
              </p>
            )}
            {status === 'paused' && (
              <p className="text-yellow-600 font-medium">
                Recording paused
              </p>
            )}
            {status === 'stopped' && (
              <p className="text-green-600 font-medium">
                Recording complete! Click "Upload & Process" to continue
              </p>
            )}
            {status === 'uploading' && (
              <p className="text-blue-600 font-medium">
                Uploading recording...
              </p>
            )}
            {status === 'processing' && (
              <p className="text-green-600 font-medium">
                Upload successful! Redirecting to dashboard...
              </p>
            )}
          </div>

          {/* Real-time Transcript (placeholder for future) */}
          {transcript && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700"
            >
              <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
                Live Transcription
              </h3>
              <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                {transcript}
              </p>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
}