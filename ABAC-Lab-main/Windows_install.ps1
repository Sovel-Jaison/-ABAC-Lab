#FOR WINDOWS ONLY

Write-Host "Installing ABAC Lab..."

# Step 1: Check if Python is installed
# This step ensures that Python is installed on the system.
# The Get-Command cmdlet is used to check if 'python' is recognized.
# If Python is not found, the script exits with an error message.
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "Python is not installed. Please install Python and try again."
    Exit # Stops the script from continuing.
}   

# Step 2: Create Virtual Environment   
# Virtual environments help isolate dependencies, ensuring they do not
# interfere with the system-wide Python installation.
# This also prevents conflicts with other Python projects.
#
# NOTE: If an antivirus or execution policy restriction exists, the virtual 
# environment might fail to be created. Adjust PowerShell policies if necessary.
Write-Host "Setting up virtual environment..."
python -m venv venv
if (-not (Test-Path "venv")) {
    Write-Host "Failed to create virtual environment. Exiting."
    Exit  # Stops the script if the virtual environment was not created
}

# Step 3: Activate Virtual Environment
# This step activates the virtual environment.
#
# NOTE: Some Windows security policies prevent script execution.
# The "Set-ExecutionPolicy" command temporarily allows this for the current session.
Write-Host "Activating virtual environment..."
Set-ExecutionPolicy Unrestricted -Scope Process -Force # Temporarily allow scripts
. .\venv\Scripts\Activate.ps1  # Activate the virtual environment

# Step 4: Upgrade pip and install dependencies
Write-Host "Installing required Python packages (pywin32, winshell)..."
python -m pip install --upgrade pip
pip install pywin32 winshell
Write-Host "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
pip install -r requirements.txt


# Step 4: Create Desktop Shortcut 
# This step runs `create_shortcut.py`, which generates a shortcut
# to launch the application from the Windows desktop.
Write-Host "Creating desktop shortcut..."
python create_shortcut.py
Write-Host "Your Windows installation complete! You can now launch ABAC Lab from your desktop shortcut."

