#!/bin/bash

# Change directory to the script's location
# This ensures the script runs from the correct directory, no matter where it's executed from.
cd "$(dirname "$0")"

# Activate the virtual environment
# This loads the dependencies installed in `venv` instead of using system-wide Python packages.
echo "Activating virtual environment..."
source venv/bin/activate

# Set environment variables required for Qt applications to run properly
export QT_QPA_PLATFORM=xcb  # Ensures compatibility with Linux desktop environments
export QT_QPA_PLATFORMTHEME=qt5ct  # Sets Qt theme to match system settings

# Print debugging information (optional)
# This helps confirm that the virtual environment is correctly activated.
echo "Using Python from: $(which python3)"
echo "Virtual Environment Path: ${VIRTUAL_ENV:-Not Activated}"

# Launch the main application (frontend.py) using the Python interpreter from the virtual environment
python3 gui.py
