# setup.py
#!/usr/bin/env python3
import subprocess
import os
import sys
import platform
import shutil

def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    return version

def setup_virtual_environment():
    if os.path.exists("venv"):
        print("Removing existing virtual environment...")
        shutil.rmtree("venv")
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Get the pip path
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip")
        activate_path = os.path.join("venv", "Scripts", "activate")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        activate_path = os.path.join("venv", "bin", "activate")
    
    print("Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"])
    
    print("Installing requirements...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    return activate_path

def setup_project_structure():
    directories = [
        "logs",
        "config",
        "models",
        "recordings"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def create_config_file():
    config = """
{
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
        "enable_object_detection": false
    }
}
"""
    with open("config/config.json", "w") as f:
        f.write(config)

def main():
    print("Setting up Tello Drone Control System...")
    
    # Check Python version
    version = check_python_version()
    print(f"Python version {version.major}.{version.minor}.{version.micro} detected")
    
    # Setup project structure
    setup_project_structure()
    
    # Create config file
    create_config_file()
    
    # Setup virtual environment
    activate_path = setup_virtual_environment()
    
    print("\nSetup completed successfully!")
    print("\nTo activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"    {activate_path}")
    else:
        print(f"    source {activate_path}")
    
    print("\nTo start the server:")
    print("    python main.py")

if __name__ == "__main__":
    main()