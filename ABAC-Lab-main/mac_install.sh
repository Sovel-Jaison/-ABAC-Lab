#!/bin/bash
 
# Display message about installing the ABAC Lab for macOS
echo "Installing ABAC Lab for macOS..."
 
# Step 1: Check if Homebrew is Installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed."
    echo "Would you like to install Homebrew now? (y/n)"
    read -r install_brew
 
    # Install Homebrew if the user agrees
    if [[ "$install_brew" == "y" || "$install_brew" == "Y" ]]; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # Here is the Homebrew documanetation link https://docs.brew.sh/Installation
 
        # Ensure Homebrew is available in the current session
        eval "$(/opt/homebrew/bin/brew shellenv)" || eval "$(/usr/local/bin/brew shellenv)"
 
        echo "Homebrew installed successfully!"
    else
        echo "Homebrew is required for this installation. Exiting."
        exit 1
    fi
else
    echo "Homebrew is already installed!"
fi
 
# Step 2: Install Dependencies with Homebrew
echo "Installing required system dependencies using Homebrew..."
brew update
brew install python3 qt pyqt
 
# Step 3: Ensure Installation Directory is Correct
INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"  # Get the script's directory
echo "Installation directory: $INSTALL_DIR"
cd "$INSTALL_DIR"
 
# Step 4: Create a Virtual Environment (venv) in the Correct Location
echo "Setting up virtual environment..."
rm -rf "$INSTALL_DIR/venv"  # Remove old virtual environment if exists
python3 -m venv "$INSTALL_DIR/venv"  # Create a new virtual environment
 
# Check if the virtual environment was successfully created
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "Error: Virtual environment creation failed."
    exit 1
fi
 
# Step 5: Activate the Virtual Environment
echo "Activating virtual environment..."
source "$INSTALL_DIR/venv/bin/activate"
 
# Display virtual environment path
VENV_PATH=$(python3 -c "import sys; print(sys.prefix)")
echo "Virtual environment successfully activated!"
echo "Virtual environment path: $VENV_PATH"
 
# Step 6: Install Python Dependencies in venv
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
 
# Step 7: Create macOS Desktop Shortcut
# Ensure `mac_run_app.sh` Exists & Set Permissions
if [ -f "mac_run_app.sh" ]; then
    echo "mac_run_app.sh already exists. Ensuring correct permissions..."
else
    echo "Error: mac_run_app.sh not found! Please create it manually or re-run installation."
    exit 1
fi
 
chmod +x mac_run_app.sh
echo "mac_run_app.sh is now executable!"
echo "Your macOS installation is complete!"
echo "To run the application, use: ./mac_run_app.sh"
echo "Virtual Environment Path: $VENV_PATH"
