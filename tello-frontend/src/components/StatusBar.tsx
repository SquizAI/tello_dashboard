// src/components/StatusBar.tsx
import React from 'react';
import { Card } from '@/components/ui/card';
import { Wifi, Battery, Thermometer } from 'lucide-react';

interface StatusBarProps {
  isConnected: boolean;
  batteryLevel?: number;
  temperature?: number;
}

export function StatusBar({ isConnected, batteryLevel = 0, temperature = 0 }: StatusBarProps) {
  return (
    <Card className="bg-white dark:bg-gray-800 p-4 shadow-lg">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Wifi className={`w-5 h-5 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
          <span className={`font-medium ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Battery className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            <span className="font-medium">{batteryLevel}%</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Thermometer className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            <span className="font-medium">{temperature}°C</span>
          </div>
        </div>
      </div>
    </Card>
  );
}