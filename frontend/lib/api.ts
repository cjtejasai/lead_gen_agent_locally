/**
 * Centralized API client configuration
 * All API calls should go through this module
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export { API_URL }

/**
 * Generic API client with common HTTP methods
 */
export const apiClient = {
  /**
   * POST request
   */
  async post(endpoint: string, data: any, options?: RequestInit) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      body: JSON.stringify(data),
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  },

  /**
   * GET request
   */
  async get(endpoint: string, options?: RequestInit) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  },

  /**
   * PUT request
   */
  async put(endpoint: string, data: any, options?: RequestInit) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      body: JSON.stringify(data),
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  },

  /**
   * DELETE request
   */
  async delete(endpoint: string, options?: RequestInit) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  },
}

/**
 * Helper to add auth token to requests
 */
export function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}