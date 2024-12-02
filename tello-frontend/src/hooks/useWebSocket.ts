// hooks/useWebSocket.ts
import { useState, useEffect, useCallback } from 'react';

interface DroneState {
  battery: number;
  temperature: number;
  height: number;
  speed: {
    x: number;
    y: number;
    z: number;
  };
  flight_time: number;
}

export function useWebSocket() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [droneState, setDroneState] = useState<DroneState | null>(null);
  const [videoFrame, setVideoFrame] = useState<string | null>(null);

  const connect = useCallback(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onopen = () => {
      setIsConnected(true);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'state_update') {
        setDroneState(data.data);
      } else if (data.type === 'video_frame') {
        setVideoFrame(data.data.frame);
      }
    };

    websocket.onclose = () => {
      setIsConnected(false);
    };

    setWs(websocket);
  }, []);

  const disconnect = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
    }
  }, [ws]);

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  return {
    isConnected,
    droneState,
    videoFrame,
    connect,
    disconnect
  };
}