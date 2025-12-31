import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        // Reconnexion automatique après 3 secondes
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      setIsConnected(false);
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(message);
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return { isConnected, lastMessage, sendMessage, disconnect, connect };
}

