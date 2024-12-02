# backend/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from djitellopy import Tello
import cv2
import numpy as np
import asyncio
import base64
import json
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
tello = None
connected = False
video_stream_active = False
tracking_active = False
takeoff_done = False
tape_detected = False

class DroneState:
    def __init__(self):
        self.battery = 0
        self.temperature = 0
        self.flight_time = 0
        self.height = 0
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0

drone_state = DroneState()

# Initialize drone
def initialize_drone():
    global tello, connected
    try:
        tello = Tello()
        tello.connect()
        battery = tello.get_battery()
        print("Battery level: {}%".format(battery))
        
        if battery < 5:
            print("Battery too low for flight. Please charge the drone.")
            return {"status": "error", "message": "Battery too low"}
        
        connected = True
        return {"status": "success", "message": "Drone connected successfully"}
    except Exception as e:
        return {"status": "error", "message": "Failed to connect: " + str(e)}

def detect_black_tape(frame):
    global tape_detected
    
    # Resize the frame for better performance
    frame_resized = cv2.resize(frame, (640, 480))

    # Convert to grayscale
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply threshold to detect dark areas (black tape)
    _, thresholded = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the black areas
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If black tape is found, process the contour
    if contours:
        # Find the largest contour by area (assuming it's the tape)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Draw the contour and bounding box if it's sufficiently large
        if cv2.contourArea(largest_contour) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(frame_resized, "Black Tape", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            tape_detected = True
            return frame_resized, (x + w // 2, y + h // 2)
    
    tape_detected = False
    return frame_resized, None

# API Routes
@app.post("/connect")
def connect():
    return initialize_drone()

@app.post("/disconnect")
def disconnect():
    global tello, connected
    try:
        if tello:
            tello.end()
            connected = False
        return {"status": "success", "message": "Drone disconnected successfully"}
    except Exception as e:
        return {"status": "error", "message": "Failed to disconnect: " + str(e)}

@app.post("/takeoff")
def takeoff():
    global tello, takeoff_done
    try:
        if tello and connected:
            tello.takeoff()
            time.sleep(5)  # Give the drone time to stabilize
            tello.move_up(30)
            takeoff_done = True
            return {"status": "success", "message": "Takeoff successful"}
    except Exception as e:
        return {"status": "error", "message": "Takeoff failed: " + str(e)}

@app.post("/land")
def land():
    global tello, takeoff_done
    try:
        if tello and connected:
            tello.land()
            takeoff_done = False
            return {"status": "success", "message": "Landing successful"}
    except Exception as e:
        return {"status": "error", "message": "Landing failed: " + str(e)}

@app.post("/move")
def move(direction: str, distance: int):
    global tello
    try:
        if tello and connected:
            if direction == "up":
                tello.move_up(distance)
            elif direction == "down":
                tello.move_down(distance)
            elif direction == "left":
                tello.move_left(distance)
            elif direction == "right":
                tello.move_right(distance)
            elif direction == "forward":
                tello.move_forward(distance)
            elif direction == "back":
                tello.move_back(distance)
            return {"status": "success", "message": "Moved " + direction}
    except Exception as e:
        return {"status": "error", "message": "Movement failed: " + str(e)}

@app.post("/rotate")
def rotate(direction: str, degrees: int):
    global tello
    try:
        if tello and connected:
            if direction == "clockwise":
                tello.rotate_clockwise(degrees)
            else:
                tello.rotate_counter_clockwise(degrees)
            return {"status": "success", "message": "Rotation successful"}
    except Exception as e:
        return {"status": "error", "message": "Rotation failed: " + str(e)}

@app.post("/flip")
def flip(direction: str):
    global tello
    try:
        if tello and connected:
            if direction == "forward":
                tello.flip_forward()
            elif direction == "back":
                tello.flip_back()
            elif direction == "left":
                tello.flip_left()
            elif direction == "right":
                tello.flip_right()
            return {"status": "success", "message": "Flip successful"}
    except Exception as e:
        return {"status": "error", "message": "Flip failed: " + str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        if tello:
            tello.streamon()
            
        while True:
            if tello and connected:
                # Update drone state
                drone_state.battery = tello.get_battery()
                drone_state.temperature = tello.get_temperature()
                drone_state.flight_time = tello.get_flight_time()
                drone_state.height = tello.get_height()
                drone_state.speed_x = tello.get_speed_x()
                drone_state.speed_y = tello.get_speed_y()
                drone_state.speed_z = tello.get_speed_z()

                # Send state update
                await websocket.send_text(json.dumps({
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
                        }
                    }
                }))

                # Get and process video frame
                frame = tello.get_frame_read().frame
                if frame is not None:
                    # Detect black tape
                    frame_with_tape, tape_center = detect_black_tape(frame)
                    
                    # Convert frame to base64
                    _, buffer = cv2.imencode('.jpg', frame_with_tape)
                    base64_frame = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send frame
                    await websocket.send_text(json.dumps({
                        "type": "video_frame",
                        "data": base64_frame,
                        "tape_detected": tape_detected,
                        "tape_center": tape_center if tape_center else None
                    }))
            
            await asyncio.sleep(0.1)
    except Exception as e:
        print("WebSocket error: " + str(e))
    finally:
        if tello:
            tello.streamoff()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)