# README.md
# Tello Drone Control System

A full-stack application for controlling DJI Tello drones with advanced features including object tracking, video streaming, and telemetry monitoring.

## Features

- Real-time video streaming with object detection
- Advanced flight controls
- Telemetry monitoring
- Object tracking
- Black line following
- Emergency protocols
- Battery monitoring
- Temperature monitoring
- Speed control
- WebSocket communication for real-time updates

## Prerequisites

### Backend Requirements
- Python 3.8+
- OpenCV
- DJITelloPy
- FastAPI
- Ultralytics YOLOv8
- Numpy

### Frontend Requirements
- Node.js 16+
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components

## Installation

1. Clone the repository:
```bash
git clone https://github.com/squizai/tello-drone-control.git
cd tello-drone-control
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
tello-drone-control/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── models/
│       └── yolov8n.pt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DroneController.tsx
│   │   │   ├── DroneControlPanel.tsx
│   │   │   ├── StatusBar.tsx
│   │   │   ├── TelemetryPanel.tsx
│   │   │   └── VideoFeed.tsx
│   │   ├── hooks/
│   │   │   ├── useDroneCommands.ts
│   │   │   └── useWebSocket.ts
│   │   └── App.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md
```

## Safety Features

The application includes several safety features:

1. Battery level monitoring with automatic landing when critical
2. Connection status monitoring
3. Emergency stop functionality
4. Height and speed limitations
5. Automatic landing on connection loss
6. Temperature monitoring

## API Endpoints

### WebSocket Endpoints
- `/ws` - Main WebSocket connection for real-time updates

### REST Endpoints
- `POST /connect` - Connect to the drone
- `POST /disconnect` - Disconnect from the drone
- `POST /takeoff` - Initiate takeoff
- `POST /land` - Land the drone
- `POST /move` - Move the drone in a specified direction
- `POST /rotate` - Rotate the drone
- `POST /flip` - Perform a flip maneuver
- `POST /speed` - Set drone speed
- `POST /track_object` - Toggle object tracking

## Development

### Adding New Features

1. Create new endpoint in `backend/main.py`
2. Add corresponding command in `frontend/src/hooks/useDroneCommands.ts`
3. Create UI component in `frontend/src/components/`
4. Update `DroneController.tsx` to include new feature

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Troubleshooting

Common issues and solutions:

1. Connection Issues
   - Ensure the drone is powered on
   - Check WiFi connection to the drone
   - Verify the backend server is running

2. Video Stream Issues
   - Restart the drone
   - Reconnect to the drone's WiFi
   - Check backend console for errors

3. Control Issues
   - Ensure battery level is sufficient
   - Verify connection status
   - Check for error messages in the console

## License

MIT License

## Acknowledgments

- DJI Tello SDK
- OpenCV
- Ultralytics YOLOv8
- FastAPI
- React
- shadcn/ui