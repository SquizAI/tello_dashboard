// src/components/DroneController.tsx
import React from 'react';
import { useToast } from '@/components/ui/use-toast';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useDroneCommands } from '@/hooks/useDroneCommands';
import { DroneControlPanel } from './DroneControlPanel';
import { VideoFeed } from './VideoFeed';
import { TelemetryPanel } from './TelemetryPanel';
import { StatusBar } from './StatusBar';

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

export default function DroneController() {
  const { toast } = useToast();
  const { 
    isConnected, 
    droneState, 
    videoFrame,
    connect: wsConnect,
    disconnect: wsDisconnect 
  } = useWebSocket();
  
  const {
    connect,
    disconnect,
    takeoff,
    land,
    move,
    rotate,
    flip,
    setSpeed,
    toggleTracking
  } = useDroneCommands();

  const handleConnect = async () => {
    try {
      await connect();
      await wsConnect();
      toast({
        title: "Connected",
        description: "Successfully connected to the drone.",
        variant: "default"
      });
    } catch (error: unknown) {
      toast({
        title: "Connection Failed",
        description: error instanceof Error ? error.message : "Failed to connect",
        variant: "destructive"
      });
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnect();
      await wsDisconnect();
      toast({
        title: "Disconnected",
        description: "Successfully disconnected from the drone.",
        variant: "default"
      });
    } catch (error: unknown) {
      toast({
        title: "Disconnection Failed",
        description: error instanceof Error ? error.message : "Failed to disconnect",
        variant: "destructive"
      });
    }
  };

  const handleMove = async (direction: string, distance: number) => {
    try {
      await move({ direction, distance });
    } catch (error: unknown) {
      toast({
        title: "Movement Failed",
        description: error instanceof Error ? error.message : "Failed to move",
        variant: "destructive"
      });
    }
  };

  const handleRotate = async (direction: string, degrees: number) => {
    try {
      await rotate({ direction, degrees });
    } catch (error: unknown) {
      toast({
        title: "Rotation Failed",
        description: error instanceof Error ? error.message : "Failed to rotate",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-4 p-4">
      <StatusBar 
        isConnected={isConnected}
        batteryLevel={droneState?.battery}
        temperature={droneState?.temperature}
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <VideoFeed videoFrame={videoFrame} />
        
        <div className="space-y-4">
          <DroneControlPanel
            isConnected={isConnected}
            onConnect={handleConnect}
            onDisconnect={handleDisconnect}
            onTakeoff={takeoff}
            onLand={land}
            onMove={handleMove}
            onRotate={handleRotate}
            onFlip={flip}
            onSpeedChange={setSpeed}
            onToggleTracking={toggleTracking}
          />
          
          <TelemetryPanel
            height={droneState?.height}
            speed={droneState?.speed}
            flightTime={droneState?.flight_time}
          />
        </div>
      </div>
    </div>
  );
}