import { useState, useEffect, useRef } from 'react'

/**
 * Custom React hook for live WebSocket task lifecycle streaming.
 * @param {string} taskId - The ID of the task to subscribe to.
 */
export function useTaskStream(taskId) {
  const [events, setEvents] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [latestEvent, setLatestEvent] = useState(null)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!taskId) return

    const wsUrl = `ws://localhost:8000/ws/tasks/${taskId}`
    const socket = new WebSocket(wsUrl)
    wsRef.current = socket

    socket.onopen = () => {
      setIsConnected(true)
    }

    socket.onmessage = (messageEvent) => {
      try {
        const data = JSON.parse(messageEvent.data)
        setLatestEvent(data)
        setEvents((prev) => [...prev, data])
      } catch (err) {
        console.error('Failed to parse WebSocket message', err)
      }
    }

    socket.onclose = () => {
      setIsConnected(false)
    }

    socket.onerror = (err) => {
      console.warn('WebSocket connection error', err)
      setIsConnected(false)
    }

    return () => {
      socket.close()
    }
  }, [taskId])

  return { events, isConnected, latestEvent }
}

export default useTaskStream
