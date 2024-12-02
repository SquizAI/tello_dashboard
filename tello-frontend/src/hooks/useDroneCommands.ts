// hooks/useDroneCommands.ts
import { useMutation } from 'react-query';

const API_BASE = 'http://localhost:8000';

async function fetchWithBody(endpoint: string, body: any = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  
  if (!response.ok) {
    throw new Error('Command failed');
  }
  
  return response.json();
}

export function useDroneCommands() {
  const connect = () => fetchWithBody('/connect');
  const disconnect = () => fetchWithBody('/disconnect');
  const takeoff = () => fetchWithBody('/takeoff');
  const land = () => fetchWithBody('/land');
  const move = (direction: string, distance: number) => 
    fetchWithBody('/move', { direction, distance });
  const rotate = (direction: string, degrees: number) =>
    fetchWithBody('/rotate', { direction, degrees });
  const flip = (direction: string) =>
    fetchWithBody('/flip', { direction });
  const setSpeed = (speed: number) =>
    fetchWithBody('/speed', { speed });
  const toggleTracking = (enabled: boolean) =>
    fetchWithBody('/track_object', { enabled });

  return {
    connect: useMutation(connect).mutateAsync,
    disconnect: useMutation(disconnect).mutateAsync,
    takeoff: useMutation(takeoff).mutateAsync,
    land: useMutation(land).mutateAsync,
    move: useMutation(
      ({ direction, distance }: { direction: string; distance: number }) =>
        move(direction, distance)
    ).mutateAsync,
    rotate: useMutation(
      ({ direction, degrees }: { direction: string; degrees: number }) =>
        rotate(direction, degrees)
    ).mutateAsync,
    flip: useMutation(flip).mutateAsync,
    setSpeed: useMutation(setSpeed).mutateAsync,
    toggleTracking: useMutation(toggleTracking).mutateAsync,
  };
}