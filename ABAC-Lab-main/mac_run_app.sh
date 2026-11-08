#!/bin/bash

# Change directory to the script's location
cd "$(dirname "$0")"


# Ensure the script is executable
chmod +x "$0"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if the virtual environment is properly activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Error: Virtual environment is not activated!"
    exit 1
fi

# Set Qt Platform to "cocoa" to prevent errors related to Qt on macOS
export QT_QPA_PLATFORM=cocoa
export QT_QPA_PLATFORM_PLUGIN_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/PyQt5/Qt5/plugins/platforms/"

# Display debugging information
echo "Using Python from: $(which python3)"
echo "Virtual Environment Path: $VIRTUAL_ENV"
echo "QT Platform Plugin Path: $QT_QPA_PLATFORM_PLUGIN_PATH"
echo "QT Platform: $QT_QPA_PLATFORM"

# Run the main application (GUI)
exec python3 gui.py
