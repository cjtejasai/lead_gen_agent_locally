'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, ArrowRight, Mail, Lock, User, MapPin, Eye, EyeOff } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

export default function SignupPage() {
  const router = useRouter()
  const [step, setStep] = useState(1) // 1: Basic Info, 2: Interests
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Form data
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    location: '',
    interests: [] as string[],
    lookingFor: [] as string[]
  })

  const interestOptions = [
    'AI & Machine Learning',
    'Blockchain & Crypto',
    'SaaS',
    'Fintech',
    'Healthcare',
    'E-commerce',
    'Marketing',
    'Sales',
    'Investment',
    'Partnerships',
    'Hiring',
    'Mentorship',
    'Funding',
    'Product Development'
  ]

  const lookingForOptions = [
    'Investors',
    'Co-founders',
    'Business Partners',
    'Customers',
    'Mentors',
    'Job Opportunities',
    'Collaboration',
    'Networking'
  ]

  const toggleInterest = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }))
  }

  const toggleLookingFor = (item: string) => {
    setFormData(prev => ({
      ...prev,
      lookingFor: prev.lookingFor.includes(item)
        ? prev.lookingFor.filter(i => i !== item)
        : [...prev.lookingFor, item]
    }))
  }

  const handleNextStep = () => {
    if (!formData.fullName || !formData.email || !formData.password) {
      setError('Please fill in all required fields')
      return
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setError('')
    setStep(2)
  }

  const handleSignup = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          full_name: formData.fullName,
          location: formData.location,
          interests: formData.interests,
          looking_for: formData.lookingFor
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Signup failed')
      }

      const data = await response.json()

      // Store token
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      // Redirect to agent working page
      router.push('/onboarding/agent-working')
    } catch (err: any) {
      setError(err.message || 'Failed to create account')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 dark:from-gray-950 dark:via-purple-950/20 dark:to-gray-950 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <Image
              src="/lyncsea-logo.png"
              alt="Lyncsea"
              width={120}
              height={120}
              className="rounded-lg"
            />
            <span className="text-4xl font-bold text-gradient tracking-tight">Lyncsea</span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {step === 1 ? 'Create Your Account' : 'Tell Us About Yourself'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {step === 1
              ? 'Join Lyncsea and start discovering valuable connections'
              : 'Help our AI find the perfect events and connections for you'
            }
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className={`w-20 h-2 rounded-full transition-colors ${step >= 1 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
          <div className={`w-20 h-2 rounded-full transition-colors ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
        </div>

        {/* Form Card */}
        <div className="glass-effect rounded-2xl p-8 shadow-lg">
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          {step === 1 ? (
            // Step 1: Basic Information
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Full Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={formData.fullName}
                    onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    placeholder="John Doe"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    placeholder="john@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full pl-10 pr-12 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    placeholder="At least 8 characters"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Location (Optional)
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    placeholder="San Francisco, CA"
                  />
                </div>
              </div>

              <button
                onClick={handleNextStep}
                className="w-full py-3 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-lg font-semibold hover:shadow-lg transition-shadow flex items-center justify-center gap-2"
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          ) : (
            // Step 2: Interests & Goals
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  What are your interests? (Select all that apply)
                </label>
                <div className="flex flex-wrap gap-2">
                  {interestOptions.map((interest) => (
                    <button
                      key={interest}
                      onClick={() => toggleInterest(interest)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                        formData.interests.includes(interest)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  What are you looking for? (Select all that apply)
                </label>
                <div className="flex flex-wrap gap-2">
                  {lookingForOptions.map((item) => (
                    <button
                      key={item}
                      onClick={() => toggleLookingFor(item)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                        formData.lookingFor.includes(item)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 border border-gray-200 dark:border-gray-700 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleSignup}
                  disabled={loading}
                  className="flex-1 py-3 bg-gradient-to-r from-blue-900 to-cyan-600 text-white rounded-lg font-semibold hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </button>
              </div>
            </div>
          )}

          {/* Login Link */}
          <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-600 hover:text-blue-700 font-semibold">
              Log in
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}