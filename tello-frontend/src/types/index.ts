// src/types/index.ts
export interface DroneState {
    battery?: number;
    temperature?: number;
    height?: number;
    speed?: {
      x: number;
      y: number;
      z: number;
    };
    flight_time?: number;
  }
  
  export interface DroneControlPanelProps {
    isConnected: boolean;
    onConnect: () => Promise<void>;
    onDisconnect: () => Promise<void>;
    onTakeoff: () => Promise<void>;
    onLand: () => Promise<void>;
    onMove: (direction: string, distance: number) => Promise<void>;
    onRotate: (direction: string, degrees: number) => Promise<void>;
    onFlip: (direction: string) => Promise<void>;
    onSpeedChange: (speed: number) => Promise<void>;
    onToggleTracking: (enabled: boolean) => Promise<void>;
  }