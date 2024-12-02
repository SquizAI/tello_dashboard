// src/components/DroneControlPanel.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import {
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  RotateCcw,
  RotateCw,
  Gamepad2,
  Eye
} from 'lucide-react';

interface DroneControlPanelProps {
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

export function DroneControlPanel({
  isConnected,
  onConnect,
  onDisconnect,
  onTakeoff,
  onLand,
  onMove,
  onRotate,
  onFlip,
  onSpeedChange,
  onToggleTracking
}: DroneControlPanelProps) {
  const [speed, setSpeed] = useState(50);
  const [isTracking, setIsTracking] = useState(false);

  const handleSpeedChange = (value: number[]) => {
    const newSpeed = value[0];
    setSpeed(newSpeed);
    onSpeedChange(newSpeed);
  };

  const handleToggleTracking = () => {
    setIsTracking(!isTracking);
    onToggleTracking(!isTracking);
  };

  return (
    <Card className="bg-white dark:bg-gray-800">
      <CardHeader>
        <CardTitle>Drone Controls</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Connection Controls */}
        <div className="flex space-x-4">
          <Button
            className="flex-1"
            variant={isConnected ? "destructive" : "default"}
            onClick={isConnected ? onDisconnect : onConnect}
          >
            {isConnected ? 'Disconnect' : 'Connect'}
          </Button>
          
          <Button
            className="flex-1"
            variant="default"
            disabled={!isConnected}
            onClick={isConnected ? onLand : onTakeoff}
          >
            {isConnected ? 'Land' : 'Take Off'}
          </Button>
        </div>

        {/* Movement Controls */}
        <div className="grid grid-cols-3 gap-2 place-items-center">
          <div />
          <Button
            variant="outline"
            size="icon"
            disabled={!isConnected}
            onClick={() => onMove('forward', 30)}
          >
            <ArrowUp className="h-6 w-6" />
          </Button>
          <div />
          
          <Button
            variant="outline"
            size="icon"
            disabled={!isConnected}
            onClick={() => onMove('left', 30)}
          >
            <ArrowLeft className="h-6 w-6" />
          </Button>
          
          <Button
            variant="outline"
            size="icon"
            disabled={!isConnected}
            onClick={() => onMove('down', 30)}
          >
            <ArrowDown className="h-6 w-6" />
          </Button>
          
          <Button
            variant="outline"
            size="icon"
            disabled={!isConnected}
            onClick={() => onMove('right', 30)}
          >
            <ArrowRight className="h-6 w-6" />
          </Button>
          
          <div />
          <div className="flex space-x-4">
            <Button
              variant="outline"
              size="icon"
              disabled={!isConnected}
              onClick={() => onRotate('counterclockwise', 90)}
            >
              <RotateCcw className="h-6 w-6" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              disabled={!isConnected}
              onClick={() => onRotate('clockwise', 90)}
            >
              <RotateCw className="h-6 w-6" />
            </Button>
          </div>
          <div />
        </div>

        {/* Speed Control */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Speed</span>
            <span className="text-sm font-medium">{speed}%</span>
          </div>
          <Slider
            value={[speed]}
            onValueChange={handleSpeedChange}
            min={0}
            max={100}
            step={10}
            disabled={!isConnected}
          />
        </div>

        {/* Advanced Controls */}
        <div className="grid grid-cols-2 gap-4">
          <Button
            variant="outline"
            disabled={!isConnected}
            onClick={() => onFlip('forward')}
            className="flex items-center justify-center space-x-2"
          >
            <Gamepad2 className="h-4 w-4" />
            <span>Flip Forward</span>
          </Button>
          
          <Button
            variant="outline"
            disabled={!isConnected}
            onClick={handleToggleTracking}
            className={`flex items-center justify-center space-x-2 ${
              isTracking ? 'bg-primary text-white' : ''
            }`}
          >
            <Eye className="h-4 w-4" />
            <span>{isTracking ? 'Stop Tracking' : 'Track Object'}</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}