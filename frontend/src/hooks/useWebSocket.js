import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/telemetry';

export function useWebSocket(onMessageReceived) {
  const [connectionStatus, setConnectionStatus] = useState('DISCONNECTED'); // CONNECTED, CONNECTING, RECONNECTING, DISCONNECTED
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);
  const isComponentMounted = useRef(true);

  const connect = useCallback(() => {
    if (!isComponentMounted.current) return;
    
    // Close existing socket if any
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    setConnectionStatus(retryCountRef.current > 0 ? 'RECONNECTING' : 'CONNECTING');

    try {
      const socket = new WebSocket(WS_URL);
      wsRef.current = socket;

      socket.onopen = () => {
        if (!isComponentMounted.current) return;
        setConnectionStatus('CONNECTED');
        retryCountRef.current = 0;
      };

      socket.onmessage = (event) => {
        if (!isComponentMounted.current) return;
        try {
          const data = JSON.parse(event.data);
          if (onMessageReceived) {
            onMessageReceived(data);
          }
        } catch (err) {
          console.error('[WebSocket] JSON parse error:', err);
        }
      };

      socket.onerror = (err) => {
        console.warn('[WebSocket] Connection error:', err);
      };

      socket.onclose = () => {
        if (!isComponentMounted.current) return;
        setConnectionStatus('DISCONNECTED');
        wsRef.current = null;

        // Exponential backoff reconnect: 1s, 2s, 4s, 8s, max 10s
        const backoffDelay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
        retryCountRef.current += 1;

        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, backoffDelay);
      };
    } catch (e) {
      console.error('[WebSocket] Setup exception:', e);
      setConnectionStatus('DISCONNECTED');
    }
  }, [onMessageReceived]);

  useEffect(() => {
    isComponentMounted.current = true;
    connect();

    return () => {
      isComponentMounted.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { connectionStatus, reconnect: connect };
}
