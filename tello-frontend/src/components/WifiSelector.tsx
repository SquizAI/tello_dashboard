// src/components/WifiSelector.tsx
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Wifi, WifiOff, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "@/components/ui/use-toast";

interface WiFiNetwork {
  ssid: string;
  signal_strength: number;
  connected: boolean;
}

const TELLO_NETWORK_PREFIX = 'TELLO-';

export function WifiSelector() {
  const [networks, setNetworks] = useState<WiFiNetwork[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [currentNetwork, setCurrentNetwork] = useState<string>('');

  // Simulate scanning for networks
  const scanNetworks = async () => {
    setIsScanning(true);
    try {
      // In a real implementation, this would use the WebNativeAPI or a backend endpoint
      // to get the actual WiFi networks
      const simulatedNetworks: WiFiNetwork[] = [
        { ssid: 'TELLO-XX1234', signal_strength: 80, connected: false },
        { ssid: 'YourHomeNetwork', signal_strength: 90, connected: true },
        { ssid: 'TELLO-YY5678', signal_strength: 70, connected: false },
      ];
      
      setNetworks(simulatedNetworks);
      setCurrentNetwork(simulatedNetworks.find(n => n.connected)?.ssid || '');
    } catch (error) {
      toast({
        title: "Error Scanning Networks",
        description: "Failed to scan for WiFi networks.",
        variant: "destructive",
      });
    } finally {
      setIsScanning(false);
    }
  };

  const connectToNetwork = async (ssid: string) => {
    if (!ssid.startsWith(TELLO_NETWORK_PREFIX)) {
      toast({
        title: "Invalid Network",
        description: "Please select a Tello drone network.",
        variant: "destructive",
      });
      return;
    }

    try {
      // In a real implementation, this would use the WebNativeAPI or a backend endpoint
      // to connect to the WiFi network
      toast({
        title: "Connecting to Drone",
        description: `Attempting to connect to ${ssid}...`,
      });

      // Simulate connection delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      setCurrentNetwork(ssid);
      toast({
        title: "Connected",
        description: `Successfully connected to ${ssid}`,
      });
    } catch (error) {
      toast({
        title: "Connection Failed",
        description: "Failed to connect to the drone's network.",
        variant: "destructive",
      });
    }
  };

  // Initial scan
  useEffect(() => {
    scanNetworks();
  }, []);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Wifi className="h-4 w-4" />
          {currentNetwork || 'Not Connected'}
        </Button>
      </DialogTrigger>
      
      <DialogContent>
        <DialogHeader>
          <DialogTitle>WiFi Networks</DialogTitle>
          <DialogDescription>
            Connect to your Tello drone's WiFi network
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              Available Networks
            </p>
            <Button 
              variant="outline" 
              size="sm"
              onClick={scanNetworks}
              disabled={isScanning}
            >
              {isScanning ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Refresh'
              )}
            </Button>
          </div>

          <div className="space-y-2">
            {networks.map((network) => (
              <Card
                key={network.ssid}
                className={`cursor-pointer transition-colors hover:bg-accent ${
                  network.connected ? 'border-primary' : ''
                }`}
                onClick={() => connectToNetwork(network.ssid)}
              >
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    {network.connected ? (
                      <Wifi className="h-4 w-4 text-primary" />
                    ) : (
                      <WifiOff className="h-4 w-4 text-muted-foreground" />
                    )}
                    <div>
                      <p className="font-medium">{network.ssid}</p>
                      <p className="text-sm text-muted-foreground">
                        Signal: {network.signal_strength}%
                      </p>
                    </div>
                  </div>
                  {network.ssid.startsWith(TELLO_NETWORK_PREFIX) && (
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                      Drone
                    </span>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          <p className="text-xs text-muted-foreground">
            Note: Your Tello drone's network usually starts with "TELLO-"
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}