#!/bin/bash

echo "Installing ABAC Lab..."

# Step 1: Ensure Python3 is Installed
# The script checks if Python3 is installed before proceeding
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed. Please install Python3 first."
    exit 1 # Exit installation if Python3 is missing
fi

# Step 2: Install System Dependencies (For Linux users)
# This installs necessary system libraries that support Python, PyQt5, and Qt applications.
echo "Checking and installing required system dependencies..."
if [ -x "$(command -v apt)" ]; then
    sudo apt update
    sudo apt install -y python3-venv python3-pip libxcb-xinerama0 libxkbcommon-x11-0 libxcb1 libx11-xcb1 libxcb-render0 libxcb-shape0 libxcb-shm0
fi

# Step 3: Create a Virtual Environment
# The virtual environment (venv) is used to manage dependencies locally, avoiding conflicts with system-wide packages.
echo "Setting up virtual environment..."
rm -rf venv  # Remove old venv if exists
python3 -m venv venv # Create a new virtual environment

# Check if the virtual environment was created successfully
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment creation failed."
    exit 1
fi

# Step 4: Activate the Virtual Environment
# This ensures that all installed dependencies are contained within the project's `venv`.
echo "Activating virtual environment..."
source venv/bin/activate

# Step 5: Upgrade pip and Install Dependencies
# Upgrading pip ensures we have the latest package manager before installing dependencies.
echo "Installing dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt # Install all required packages from `requirements.txt`

# Step 6: Verify PyQt5 Installation
# This test ensures that PyQt5 (the GUI framework) is installed and working properly.
echo "Checking PyQt5 installation..."
python3 -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 is installed correctly!')"

## Step 7: Set Qt Environment Variables to Fix GUI Issues
# Some Linux distributions need these settings for PyQt5 applications to work correctly.
echo "Setting QT_QPA_PLATFORM=xcb..."
echo 'export QT_QPA_PLATFORM=xcb' >> ~/.bashrc
export QT_QPA_PLATFORM=xcb

# Step 8: Install Additional Qt Dependencies for GUI and Icons
# These packages improve Qt compatibility with different Linux desktop environments.
echo "Installing additional Qt dependencies for icon support..."
sudo apt install -y qt5-style-plugins qt5-gtk-platformtheme libqt5svg5 adwaita-icon-theme hicolor-icon-theme breeze-icon-theme qt5ct

# Ensure Qt applications match the system's look and feel.
echo 'export QT_QPA_PLATFORMTHEME=qt5ct' >> ~/.bashrc
export QT_QPA_PLATFORMTHEME=qt5ct

# Step 9: Create a Desktop Shortcut
# This step runs `create_shortcut.py`, which generates a `.desktop` file to launch the application from the desktop.
echo "Creating desktop shortcut..."
python3 create_shortcut.py

echo "Your Linux installation complete! You can now launch ABAC Lab from your desktop shortcut."
