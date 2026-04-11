import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws'
const RECONNECT_DELAY = 2000

/**
 * WebSocket state hook.
 * Connects to the backend WS, auto-reconnects on close.
 * Returns { state, connected }.
 */
export function useWS() {
  const [state, setState] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const timerRef = useRef(null)

  const connect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.onclose = null
      wsRef.current.close()
    }
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)

    ws.onmessage = (evt) => {
      try {
        setState(JSON.parse(evt.data))
      } catch (_) {}
    }

    ws.onclose = () => {
      setConnected(false)
      timerRef.current = setTimeout(connect, RECONNECT_DELAY)
    }

    ws.onerror = () => ws.close()
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(timerRef.current)
      if (wsRef.current) wsRef.current.onclose = null
      wsRef.current?.close()
    }
  }, [connect])

  return { state, connected }
}
