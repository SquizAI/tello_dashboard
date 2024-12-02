// components/VideoFeed.tsx
import React from 'react';

interface VideoFeedProps {
  videoFrame: string | null;
}

export function VideoFeed({ videoFrame }: VideoFeedProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Video Feed</h3>
      {videoFrame ? (
        <img
          src={`data:image/jpeg;base64,${videoFrame}`}
          alt="Drone video feed"
          className="w-full rounded-lg"
        />
      ) : (
        <div className="aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
          No video feed available
        </div>
      )}
    </div>
  );
}