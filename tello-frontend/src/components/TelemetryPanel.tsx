// components/TelemetryPanel.tsx
import React from 'react';
import { ArrowUp, Gauge, Clock } from 'lucide-react';

interface TelemetryPanelProps {
  height?: number;
  speed?: {
    x: number;
    y: number;
    z: number;
  };
  flightTime?: number;
}

export function TelemetryPanel({ height, speed, flightTime }: TelemetryPanelProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Telemetry</h3>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <ArrowUp className="w-5 h-5 mr-2" />
            <span>Height</span>
          </div>
          <span>{height ?? 0} cm</span>
        </div>
        
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Gauge className="w-5 h-5 mr-2" />
            <span>Speed</span>
          </div>
          <div className="text-right">
            <div>X: {speed?.x ?? 0} cm/s</div>
            <div>Y: {speed?.y ?? 0} cm/s</div>
            <div>Z: {speed?.z ?? 0} cm/s</div>
          </div>
        </div>
        
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            <span>Flight Time</span>
          </div>
          <span>{flightTime ?? 0} seconds</span>
        </div>
      </div>
    </div>
  );
}