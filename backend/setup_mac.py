# setup_mac.py
import os
import json
import sys

def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'config', 'recordings']
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
            print(f"Created directory: {dir}")

def create_config():
    """Create configuration file"""
    config = {
        "drone": {
            "min_battery": 15,
            "max_height": 200,
            "max_speed": 80,
            "safety_distance": 50
        },
        "video": {
            "width": 960,
            "height": 720,
            "fps": 30,
            "recording_path": "recordings"
        },
        "detection": {
            "tape_threshold": 60,
            "min_contour_area": 500,
            "enable_object_detection": False
        }
    }
    
    with open('config/config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("Created config file: config/config.json")

def create_requirements():
    """Create requirements.txt"""
    requirements = """
numpy==1.21.6
fastapi==0.103.2
uvicorn==0.22.0
djitellopy==2.5.0
opencv-python==4.7.0.72
websockets==10.4
    """.strip()
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("Created requirements.txt")

def main():
    print("Setting up Tello Drone Control System...")
    
    # Create project structure
    create_directories()
    create_config()
    create_requirements()
    
    print("\nSetup completed! Next steps:")
    print("\n1. Install requirements:")
    print("   pip install -r requirements.txt")
    print("\n2. Start the server:")
    print("   python main.py")

if __name__ == "__main__":
    main()