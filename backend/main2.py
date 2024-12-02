# main.py
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from djitellopy import Tello
import cv2
import numpy as np
import asyncio
import json
import time
import logging
import math
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
import threading
from queue import Queue
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/drone.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
with open('config/config.json', 'r') as f:
    CONFIG = json.load(f)

class FlightMode(Enum):
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"
    MISSION = "mission"
    FOLLOW = "follow"
    RETURN_HOME = "return_home"

class DroneState:
    def __init__(self):
        self.battery = 0
        self.temperature = 0
        self.flight_time = 0
        self.height = 0
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.acceleration_x = 0
        self.acceleration_y = 0
        self.acceleration_z = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.barometer = 0
        self.flight_mode = FlightMode.MANUAL
        self.is_flying = False
        self.mission_running = False
        self.home_point = None
        self.current_waypoint = None
        self.emergency_mode = False
        self.last_command_time = time.time()
        self.recording = False

class Waypoint:
    def __init__(self, x: int, y: int, z: int, yaw: int = 0, action: str = None):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.action = action  # Optional action to perform at waypoint

class Mission:
    def __init__(self):
        self.waypoints: List[Waypoint] = []
        self.current_index = 0
        self.is_running = False
        self.is_paused = False

class SafetySystem:
    def __init__(self):
        self.min_battery = CONFIG['drone']['min_battery']
        self.max_height = CONFIG['drone']['max_height']
        self.max_speed = CONFIG['drone']['max_speed']
        self.safety_distance = CONFIG['drone']['safety_distance']
        self.command_cooldown = 0.1  # seconds
        self.last_command_time = 0
        self.emergency_triggers = 0
        self.max_emergency_triggers = 3

    def check_battery(self, level: int) -> bool:
        if level < self.min_battery:
            logger.warning(f"Battery level critical: {level}%")
            return False
        return True

    def check_height(self, height: int) -> bool:
        if height > self.max_height:
            logger.warning(f"Height limit exceeded: {height}cm")
            return False
        return True

    def check_speed(self, speed: float) -> bool:
        if abs(speed) > self.max_speed:
            logger.warning(f"Speed limit exceeded: {speed}cm/s")
            return False
        return True

    def can_execute_command(self) -> bool:
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return False
        self.last_command_time = current_time
        return True

class VideoProcessor:
    def __init__(self):
        self.frame_width = CONFIG['video']['width']
        self.frame_height = CONFIG['video']['height']
        self.fps = CONFIG['video']['fps']
        self.recording_path = CONFIG['video']['recording_path']
        self.video_writer = None
        self.recording = False
        self.frame_queue = Queue(maxsize=30)
        self.recording_thread = None

    def start_recording(self):
        if not self.recording:
            filename = f"{self.recording_path}/flight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            self.video_writer = cv2.VideoWriter(
                filename,
                cv2.VideoWriter_fourcc(*'XVID'),
                self.fps,
                (self.frame_width, self.frame_height)
            )
            self.recording = True
            self.recording_thread = threading.Thread(target=self._record_frames)
            self.recording_thread.start()
            logger.info(f"Started recording to {filename}")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            if self.recording_thread:
                self.recording_thread.join()
            if self.video_writer:
                self.video_writer.release()
            logger.info("Stopped recording")

    def _record_frames(self):
        while self.recording:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                if self.video_writer:
                    self.video_writer.write(frame)
            else:
                time.sleep(0.01)

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        if frame is None:
            return None, {}

        # Resize frame
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))

        # Add to recording queue if recording
        if self.recording:
            if not self.frame_queue.full():
                self.frame_queue.put(frame.copy())

        # Process frame for different features
        frame_info = {}
        
        # Detect black tape
        tape_frame, tape_info = self.detect_black_tape(frame.copy())
        if tape_info:
            frame = tape_frame
            frame_info['tape'] = tape_info

        # Detect obstacles
        obstacles_frame, obstacle_info = self.detect_obstacles(frame.copy())
        if obstacle_info:
            frame = obstacles_frame
            frame_info['obstacles'] = obstacle_info

        # Add telemetry overlay
        frame = self.add_telemetry_overlay(frame)

        return frame, frame_info

    def detect_black_tape(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Threshold for black tape
            _, thresh = cv2.threshold(
                blurred,
                CONFIG['detection']['tape_threshold'],
                255,
                cv2.THRESH_BINARY_INV
            )

            # Find contours
            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > CONFIG['detection']['min_contour_area']:
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    
                    # Draw on frame
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Calculate center
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # Draw center point
                    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                    
                    return frame, {
                        'center': (center_x, center_y),
                        'width': w,
                        'height': h,
                        'area': cv2.contourArea(largest_contour)
                    }

            return frame, {}
            
        except Exception as e:
            logger.error(f"Error in tape detection: {str(e)}")
            return frame, {}

    def detect_obstacles(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use depth information if available (simulated here)
            # In reality, you'd use the drone's sensors or stereo vision
            
            # For demo, detect large objects as potential obstacles
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            obstacles = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 5000:  # Min area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(
                        frame,
                        'Obstacle',
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        2
                    )
                    obstacles.append({
                        'position': (x + w//2, y + h//2),
                        'size': (w, h),
                        'area': area
                    })
            
            return frame, {'obstacles': obstacles}
            
        except Exception as e:
            logger.error(f"Error in obstacle detection: {str(e)}")
            return frame, {}

    def add_telemetry_overlay(self, frame: np.ndarray) -> np.ndarray:
        # Add telemetry information overlay to frame
        try:
            height, width = frame.shape[:2]
            
            # Create semi-transparent overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (200, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Add text with telemetry info
            if drone_state:
                info_lines = [
                    f"BAT: {drone_state.battery}%",
                    f"ALT: {drone_state.height}cm",
                    f"SPD: {int(math.sqrt(drone_state.speed_x**2 + drone_state.speed_y**2))}cm/s",
                    f"YAW: {drone_state.yaw}°",
                    f"Mode: {drone_state.flight_mode.value}"
                ]
                
                for i, line in enumerate(info_lines):
                    cv2.putText(
                        frame,
                        line,
                        (20, 30 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )
            
            return frame
            
        except Exception as e:
            logger.error(f"Error adding telemetry overlay: {str(e)}")
            return frame

class PathPlanner:
    def __init__(self):
        self.obstacles = []
        self.waypoints = []
        self.path = []
        self.grid_size = 20  # cm
        self.safety_margin = CONFIG['drone']['safety_distance']

    def update_obstacles(self, obstacles: List[dict]):
        self.obstacles = obstacles

    def plan_path(self, start: Tuple[int, int, int], goal: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """A* pathfinding implementation"""
        # Implementation continues...
        pass

    def check_collision(self, point: Tuple[int, int, int]) -> bool:
        """Check if point collides with any known obstacles"""
        for obstacle in self.obstacles:
            pos = obstacle['position']
            size = obstacle['size']
            # Check collision accounting for safety margin
            if (abs(point[0] - pos[0]) < (size[0]/2 + self.safety_margin) and
                abs(point[1] - pos[1]) < (size[1]/2 + self.safety_margin) and
                point[2] < size[1]):
                return True
        return False

class AutonomousController:
    def __init__(self, tello: Tello):
        self.tello = tello
        self.path_planner = PathPlanner()
        self.current_mission = None
        self.home_position = None
        self.is_autonomous = False

    async def start_mission(self, mission: Mission):
        self.current_mission = mission
        self.is_autonomous = True
        
        try:
            while self.current_mission and self.is_autonomous:
                if not self.current_mission.is_paused:
                    await self.execute_next_waypoint()
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Mission error: {str(e)}")
            await self.emergency_stop()

    async def execute_next_waypoint(self):
        if not self.current_mission or self.current_mission.current_index >= len(self.current_mission.waypoints):
            return

        waypoint = self.current_mission.waypoints[self.current_mission.current_index]
        
        try:
            # Calculate path to waypoint
            current_pos = (self.tello.get_x(), self.tello.get_y(), self.tello.get_height())
            path = self.path_planner.plan_path(current_pos, (waypoint.x, waypoint.y, waypoint.z))
            
            # Execute path
            for point in path:
                if not self.is_autonomous:
                    break
                    
                # Move to point
                await self.move_to_point(point)
                
                # Check if we've reached the waypoint
                if self.check_reached_point(point):
                    # Execute waypoint action if any
                    if waypoint.action:
                        await self.execute_waypoint_action(waypoint.action)
                    
                    self.current_mission.current_index += 1
                    break
                
        except Exception as e:
            logger.error(f"Waypoint execution error: {str(e)}")
            raise

    async def move_to_point(self, point: Tuple[int, int, int]):
        """Move drone to specific point in 3D space"""
        try:
            current_x = self.tello.get_x()
            current_y = self.tello.get_y()
            current_z = self.tello.get_height()
            
            # Calculate distances
            dx = point[0] - current_x
            dy = point[1] - current_y
            dz = point[2] - current_z
            
            # Move in each axis
            if abs(dx) > 20:
                self.tello.move_right(dx) if dx > 0 else self.tello.move_left(-dx)
            if abs(dy) > 20:
                self.tello.move_forward(dy) if dy > 0 else self.tello.move_back(-dy)
            if abs(dz) > 20:
                self.tello.move_up(dz) if dz > 0 else self.tello.move_down(-dz)
                
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Movement error: {str(e)}")
            raise

    def check_reached_point(self, point: Tuple[int, int, int], threshold: int = 20) -> bool:
        """Check if drone has reached target point within threshold"""
        current_pos = (self.tello.get_x(), self.tello.get_y(), self.tello.get_height())
        return all(abs(a - b) < threshold for a, b in zip(current_pos, point))

    async def execute_waypoint_action(self, action: str):
        """Execute special action at waypoint"""
        try:
            if action == "flip":
                self.tello.flip_forward()
            elif action == "rotate360":
                self.tello.rotate_clockwise(360)
            elif action == "take_photo":
                # Implement photo capture
                pass
            elif action == "hover":
                await asyncio.sleep(5)
            
            await asyncio.sleep(1)  # Allow action to complete
            
        except Exception as e:
            logger.error(f"Waypoint action error: {str(e)}")
            raise

    async def emergency_stop(self):
        """Emergency stop procedure"""
        try:
            self.is_autonomous = False
            self.current_mission = None
            self.tello.emergency()
            logger.warning("Emergency stop initiated")
        except Exception as e:
            logger.error(f"Emergency stop error: {str(e)}")

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
tello = None
drone_state = DroneState()
safety_system = SafetySystem()
video_processor = VideoProcessor()
autonomous_controller = None

# Initialize drone
@app.post("/connect")
async def connect():
    global tello, autonomous_controller
    try:
        tello = Tello()
        tello.connect()
        
        battery = tello.get_battery()
        if not safety_system.check_battery(battery):
            raise HTTPException(status_code=400, detail="Battery too low for operation")
            
        drone_state.battery = battery
        autonomous_controller = AutonomousController(tello)
        
        logger.info("Drone connected successfully")
        return {"status": "success", "message": "Connected", "battery": battery}
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Basic flight controls
@app.post("/takeoff")
async def takeoff():
    try:
        if not safety_system.check_battery(drone_state.battery):
            raise HTTPException(status_code=400, detail="Battery too low for takeoff")
        
        tello.takeoff()
        drone_state.is_flying = True
        drone_state.home_point = (0, 0, tello.get_height())
        
        logger.info("Takeoff successful")
        return {"status": "success", "message": "Takeoff successful"}
    except Exception as e:
        logger.error(f"Takeoff error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/land")
async def land():
    try:
        tello.land()
        drone_state.is_flying = False
        logger.info("Landing successful")
        return {"status": "success", "message": "Landing successful"}
    except Exception as e:
        logger.error(f"Landing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emergency")
async def emergency():
    try:
        await autonomous_controller.emergency_stop()
        drone_state.emergency_mode = True
        return {"status": "success", "message": "Emergency stop initiated"}
    except Exception as e:
        logger.error(f"Emergency stop error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Movement controls
@app.post("/move")
async def move(direction: str, distance: int):
    try:
        if not safety_system.can_execute_command():
            raise HTTPException(status_code=429, detail="Command rate limit exceeded")
            
        if not drone_state.is_flying:
            raise HTTPException(status_code=400, detail="Drone is not flying")
            
        command_map = {
            "forward": tello.move_forward,
            "back": tello.move_back,
            "left": tello.move_left,
            "right": tello.move_right,
            "up": tello.move_up,
            "down": tello.move_down
        }
        
        if direction not in command_map:
            raise HTTPException(status_code=400, detail="Invalid direction")
            
        command_map[direction](distance)
        return {"status": "success", "message": f"Moved {direction} by {distance}cm"}
    except Exception as e:
        logger.error(f"Movement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Advanced flight features
@app.post("/start_mission")
async def start_mission(waypoints: List[dict]):
    try:
        mission = Mission()
        for wp in waypoints:
            mission.waypoints.append(
                Waypoint(wp['x'], wp['y'], wp['z'], wp.get('yaw', 0), wp.get('action'))
            )
        
        drone_state.flight_mode = FlightMode.MISSION
        await autonomous_controller.start_mission(mission)
        
        return {"status": "success", "message": "Mission started"}
    except Exception as e:
        logger.error(f"Mission start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/return_home")
async def return_home():
    try:
        if not drone_state.home_point:
            raise HTTPException(status_code=400, detail="Home point not set")
            
        drone_state.flight_mode = FlightMode.RETURN_HOME
        
        # Create a simple mission to return home
        mission = Mission()
        mission.waypoints.append(
            Waypoint(
                drone_state.home_point[0],
                drone_state.home_point[1],
                drone_state.home_point[2]
            )
        )
        
        await autonomous_controller.start_mission(mission)
        
        return {"status": "success", "message": "Returning to home point"}
    except Exception as e:
        logger.error(f"Return home error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Video controls
@app.post("/start_recording")
async def start_recording():
    try:
        video_processor.start_recording()
        return {"status": "success", "message": "Recording started"}
    except Exception as e:
        logger.error(f"Recording start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop_recording")
async def stop_recording():
    try:
        video_processor.stop_recording()
        return {"status": "success", "message": "Recording stopped"}
    except Exception as e:
        logger.error(f"Recording stop error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket handler for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        if tello:
            tello.streamon()
        
        while True:
            # Update drone state
            if tello and drone_state.is_flying:
                drone_state.battery = tello.get_battery()
                drone_state.height = tello.get_height()
                drone_state.temperature = tello.get_temperature()
                drone_state.flight_time = tello.get_flight_time()
                
                # Get speed values
                drone_state.speed_x = tello.get_speed_x()
                drone_state.speed_y = tello.get_speed_y()
                drone_state.speed_z = tello.get_speed_z()
                
                # Get attitude values
                drone_state.pitch = tello.get_pitch()
                drone_state.roll = tello.get_roll()
                drone_state.yaw = tello.get_yaw()
                
                # Check safety conditions
                if not safety_system.check_battery(drone_state.battery):
                    await return_home()
                
                if not safety_system.check_height(drone_state.height):
                    tello.move_down(30)
            
            # Process video frame
            if tello:
                frame = tello.get_frame_read().frame
                if frame is not None:
                    processed_frame, frame_info = video_processor.process_frame(frame)
                    
                    # Convert frame to base64
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    base64_frame = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send state and frame data
                    await websocket.send_json({
                        "type": "state_update",
                        "data": {
                            "battery": drone_state.battery,
                            "temperature": drone_state.temperature,
                            "flight_time": drone_state.flight_time,
                            "height": drone_state.height,
                            "speed": {
                                "x": drone_state.speed_x,
                                "y": drone_state.speed_y,
                                "z": drone_state.speed_z
                            },
                            "attitude": {
                                "pitch": drone_state.pitch,
                                "roll": drone_state.roll,
                                "yaw": drone_state.yaw
                            },
                            "mode": drone_state.flight_mode.value,
                            "is_flying": drone_state.is_flying,
                            "emergency_mode": drone_state.emergency_mode
                        }
                    })
                    
                    await websocket.send_json({
                        "type": "video_frame",
                        "data": {
                            "frame": base64_frame,
                            "info": frame_info
                        }
                    })
            
            await asyncio.sleep(0.03)  # ~30 FPS
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if tello:
            tello.streamoff()

# Main application startup
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Tello Drone Control System...")
    uvicorn.run(app, host="0.0.0.0", port=8000)