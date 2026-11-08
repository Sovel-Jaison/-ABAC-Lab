![ABAC Header](res/abac-header.png)


## 📄 Research & Publication

ABAC Lab is built on research accepted to [SACMAT 2025](https://www.sacmat.org/2025/index.php), the ACM Symposium on Access Control Models and Technologies.

Read the full paper on arXiv:  
[Access the ABAC Lab Research Publication](https://arxiv.org/abs/2505.08209)

## ABAC Lab Application Demo

Check out the full walkthrough and demonstration of the ABAC Lab application on YouTube:  
[Watch the Demo](https://youtu.be/KtmSem5jK-A)

## Table of Contents
- [Welcome to ABAC Lab](#welcome-to-abac-lab)
- [Datasets Overview](#datasets-overview)
  - [University](DATASETS/university/)
  - [Workforce](DATASETS/workforce/)
  - [Healthcare](DATASETS/healthcare/)
  - [Project Management](DATASETS/project-management/)
  - [Edocument](DATASETS/edocument/)
- [Script Building by OS](#script-building-by-os)
  - [Windows](#windows)
  - [Linux](#linux)
  - [MacOS](#macos)
- [Manual Installation](#manual-installation)
- [Troubleshooting](#troubleshooting)


# Welcome to ABAC Lab
ABAC Lab is an open-source platform designed to support researchers and policy administrators working with Attribute-Based Access Control (ABAC) policies. It provides a unified repository of standardized ABAC datasets, including both existing datasets and new ones derived from real-world case studies. The platform also offers tools for policy visualization, analysis, and debugging. ABAC Lab encourages collaboration by allowing contributions of new datasets and provides an accessible environment for benchmarking, testing, and managing ABAC policies.

# Datasets Overview
ABAC Lab includes a curated set of sample ABAC policy datasets to support analysis and benchmarking. The **University, Workforce, Healthcare, Project Management,** and **Edocument** datasets each represent different real-world access control scenarios and demonstrate the flexibility of ABAC policies across domains. Each dataset includes attribute definitions, access rules, and sample entries to facilitate exploration and experimentation. Please locate to the DATASETS folder for each dataset file and description. The description of the dataset files is available in file [.abac Files Description](DATASETS/README.md). Please refer to this format for the contributions of new datasets. The list of descriptions are also available in the following list: 

- [University](DATASETS/university/)
- [Workforce](DATASETS/workforce/)
- [Healthcare](DATASETS/healthcare/)
- [Project Management](DATASETS/project-management/)
- [Edocument](DATASETS/edocument/)


# ABAC Lab - Building Guide
## Script Building by OS

**Note:** ABAC Lab is an open-source project. If the provided installation scripts do not work as expected on your system, you are welcome to modify them to better fit your environment. Each script includes step-by-step instructions to help guide you through the installation process. Community contributions and improvements are always welcome and appreciated.

### **Windows**
1. Open **PowerShell** in the project folder.
2. Run:
   ```powershell
   .\Windows_install.ps1
**IMPORTANT**: 
- The reason why we are using PowerShell is because it's the recommended tool for running .ps1 scripts on Windows. It allows the script to perform setup tasks more smoothly, such as creating shortcuts or configuring the environment.
- If you encounter a `running script is disabled on this system` error, it might be due to your system’s execution policy settings.  Consider temporarily allowing scripts for the current session with: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`. Alternatively, you can follow the manual installation instructions if you prefer not to modify execution policies.

After successful installation, you will see the ABAC Lab application on your desktop. The script will generate a desktop shortcut for you for easy access.  

### **Linux**
1. Open **Terminal** in the project folder.
2. Run:
   ```CMD
    Please make sure `linux_install.sh` and `linux_run_app.sh` has execute privileges.
    ./linux_install.sh
After successful installation, you should see the ABAC Lab application on your desktop. You may need to allow it to launch, depending on your system settings. The script will generate a desktop shortcut for you for easy access. 

### **MacOS**
1. Open **CMD** in the project folder.
2. Run:
   ```CMD
    Please make sure `mac_install.sh` and `mac_run_app.sh` has execute privilages.
    ./mac_install.sh
    ./mac_run_app.sh 

**IMPORTANT**: In order to rerun the application, you will have to execute `./mac_run_app.sh` within the same project folder. You don't have to rerun `mac_install.sh` since the installation will be completed. 
Mac users will NOT have a shortcut created like Windows or Linux. Lastly, Qt Platform is set to "cocoa" it may take a while for it to open the application.

## Manual Installation

**Note:** All required dependencies for the ABAC Lab application are listed in the [requirements.txt](./requirements.txt) file. You can refer to it to review or manually install specific packages if needed.


### **Prerequisites**
Ensure you have the following installed:
1. Python 3.8+ (recommended for best user experience)
2. pip (comes with Python)
3. Git (to clone the repository)
4. Virtual Environment (**recommended** for dependency management)

### **Installation**
1. Make a new directory to store the cloned repository
- Within the new directory run: `git clone <repo-url>` 

**IMPORTANT**: Before installing the dependencies, you have the option to create and activate a virtual environment to install them there.

3. Install Dependencies\
      Install the required Python packages from  requirements.txt:\
   `pip install -r requirements.txt`


4. Run the Application\
      `python gui.py`


## Troubleshooting
If installation issues arise, update pip (depending on your OS):
- `python -m pip install --upgrade pip`

For Windows users, ensure `pywin32` and `winshell` are installed if needed.

Verify Python dependencies using:
- `pip list`




