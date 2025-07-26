import { createContext, useContext, useState, useEffect } from 'react'
import { useToast } from '@/hooks/use-toast'

const AuthContext = createContext({})

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      validateToken(token)
    } else {
      setLoading(false)
    }
  }, [])

  const validateToken = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData.user)
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('auth_token')
        setUser(null)
      }
    } catch (error) {
      console.error('Token validation error:', error)
      localStorage.removeItem('auth_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok) {
        localStorage.setItem('auth_token', data.access_token)
        setUser(data.user)
        toast({
          title: "Login Successful",
          description: `Welcome back, ${data.user.full_name}!`
        })
        return { success: true, user: data.user }
      } else {
        toast({
          title: "Login Failed",
          description: data.error || "Invalid credentials",
          variant: "destructive"
        })
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Login error:', error)
      toast({
        title: "Login Error",
        description: "Network error. Please try again.",
        variant: "destructive"
      })
      return { success: false, error: "Network error" }
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData) => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (response.ok) {
        localStorage.setItem('auth_token', data.access_token)
        setUser(data.user)
        toast({
          title: "Registration Successful",
          description: `Welcome to GlobalTrade AI, ${data.user.full_name}!`
        })
        return { success: true, user: data.user }
      } else {
        toast({
          title: "Registration Failed",
          description: data.error || "Registration failed",
          variant: "destructive"
        })
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Registration error:', error)
      toast({
        title: "Registration Error",
        description: "Network error. Please try again.",
        variant: "destructive"
      })
      return { success: false, error: "Network error" }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out."
    })
  }

  const updateProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`${API_BASE_URL}/users/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      })

      const data = await response.json()

      if (response.ok) {
        setUser(data.user)
        toast({
          title: "Profile Updated",
          description: "Your profile has been updated successfully."
        })
        return { success: true, user: data.user }
      } else {
        toast({
          title: "Update Failed",
          description: data.error || "Failed to update profile",
          variant: "destructive"
        })
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('Profile update error:', error)
      toast({
        title: "Update Error",
        description: "Network error. Please try again.",
        variant: "destructive"
      })
      return { success: false, error: "Network error" }
    }
  }

  const getAuthToken = () => {
    return localStorage.getItem('auth_token')
  }

  const makeAuthenticatedRequest = async (url, options = {}) => {
    const token = getAuthToken()
    if (!token) {
      throw new Error('No authentication token available')
    }

    const defaultHeaders = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    })

    // If token is expired, logout user
    if (response.status === 401) {
      logout()
      throw new Error('Authentication expired')
    }

    return response
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile,
    getAuthToken,
    makeAuthenticatedRequest
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

