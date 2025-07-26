import { createContext, useContext, useEffect, useState } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from './AuthContext'
import { useToast } from '@/hooks/use-toast'

const SocketContext = createContext({})

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000'

export function SocketProvider({ children }) {
  const [socket, setSocket] = useState(null)
  const [connected, setConnected] = useState(false)
  const [onlineUsers, setOnlineUsers] = useState([])
  const { user, getAuthToken } = useAuth()
  const { toast } = useToast()

  useEffect(() => {
    if (user && getAuthToken()) {
      initializeSocket()
    } else {
      disconnectSocket()
    }

    return () => {
      disconnectSocket()
    }
  }, [user])

  const initializeSocket = () => {
    const token = getAuthToken()
    if (!token) return

    const newSocket = io(SOCKET_URL, {
      auth: {
        token: token
      },
      transports: ['websocket', 'polling']
    })

    newSocket.on('connect', () => {
      console.log('Socket connected:', newSocket.id)
      setConnected(true)
      setSocket(newSocket)
    })

    newSocket.on('disconnect', () => {
      console.log('Socket disconnected')
      setConnected(false)
    })

    newSocket.on('connected', (data) => {
      console.log('Authentication successful:', data)
      toast({
        title: "Connected",
        description: "Real-time communication enabled"
      })
    })

    newSocket.on('error', (error) => {
      console.error('Socket error:', error)
      toast({
        title: "Connection Error",
        description: error.message || "Failed to connect to real-time services",
        variant: "destructive"
      })
    })

    // Handle new messages
    newSocket.on('new_message', (message) => {
      console.log('New message received:', message)
      // This will be handled by individual components
    })

    // Handle voice responses
    newSocket.on('voice_response', (response) => {
      console.log('Voice response received:', response)
      // This will be handled by voice components
    })

    // Handle typing indicators
    newSocket.on('user_typing', (data) => {
      console.log('User typing:', data)
      // This will be handled by chat components
    })

    // Handle notifications
    newSocket.on('notification', (notification) => {
      console.log('Notification received:', notification)
      toast({
        title: notification.title || "Notification",
        description: notification.message
      })
    })

    setSocket(newSocket)
  }

  const disconnectSocket = () => {
    if (socket) {
      socket.disconnect()
      setSocket(null)
      setConnected(false)
    }
  }

  // Chat functions
  const joinConversation = (conversationId) => {
    if (socket && connected) {
      socket.emit('join_conversation', { conversation_id: conversationId })
    }
  }

  const leaveConversation = (conversationId) => {
    if (socket && connected) {
      socket.emit('leave_conversation', { conversation_id: conversationId })
    }
  }

  const sendMessage = (messageData) => {
    if (socket && connected) {
      socket.emit('send_message', messageData)
    }
  }

  const sendTypingIndicator = (conversationId, isTyping) => {
    if (socket && connected) {
      socket.emit('typing', {
        conversation_id: conversationId,
        is_typing: isTyping
      })
    }
  }

  // Voice functions
  const startVoiceSession = (sessionConfig) => {
    if (socket && connected) {
      socket.emit('start_voice_session', sessionConfig)
    }
  }

  const sendVoiceData = (sessionId, audioData) => {
    if (socket && connected) {
      socket.emit('voice_audio_data', {
        session_id: sessionId,
        audio_data: audioData
      })
    }
  }

  const endVoiceSession = (sessionId) => {
    if (socket && connected) {
      socket.emit('end_voice_session', { session_id: sessionId })
    }
  }

  // Event listeners
  const addEventListener = (event, callback) => {
    if (socket) {
      socket.on(event, callback)
    }
  }

  const removeEventListener = (event, callback) => {
    if (socket) {
      socket.off(event, callback)
    }
  }

  const value = {
    socket,
    connected,
    onlineUsers,
    joinConversation,
    leaveConversation,
    sendMessage,
    sendTypingIndicator,
    startVoiceSession,
    sendVoiceData,
    endVoiceSession,
    addEventListener,
    removeEventListener
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}

export function useSocket() {
  const context = useContext(SocketContext)
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}

