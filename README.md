# vespCV - Asian Hornet Detection System

## Overview
The vespCV project aims to develop an automated detection system for the invasive Asian hornet (Vespa velutina). This system leverages computer vision technology to provide beekeepers and researchers with a reliable tool for monitoring and controlling hornet populations.

## Introduction
In recent years, the invasive Asian hornet (Vespa velutina) has posed a significant threat to honeybee populations and, consequently, to our ecosystems and agriculture. The `vespCV` project aims to develop an open source non-profit automated detection system that empowers beekeepers, volunteers, and researchers to combat this growing challenge effectively.

### Problem Statement
The Asian hornet threatens honeybees and can possibly disrupt local ecosystems. Beekeepers and researchers need a reliable, easy-to-use way to spot these hornets early.

### Solution Overview
`vespCV` uses a Raspberry Pi 4 and a camera to automatically spot Asian hornets. It takes pictures, checks them with a computer vision model (YOLOv11s), and alerts you if an Azian hornet is found.

## Installation Instructions
1. Install Raspberry Pi OS Bookworm.
2. Create a directory in your home folder:
   ```bash
   mkdir vespcv
   cd vespcv
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/vespCV/vespcv.git
   cd vespcv
   ```
4. Set up the virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. Create a start script:
   ```bash
   # Create a new file called start_vespcv
   nano start_vespcv
   ```
   
   Copy and paste these lines into the file:
   ```bash
   #!/bin/bash
   cd ~/vespcv
   source venv/bin/activate
   python main.py
   ```
   
   Save the file by pressing:
   - `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save
   
   Make the script executable:
   ```bash
   chmod +x start_vespcv
   ```
6. Email Configuration (Optional)

If you don’t want email alerts, or if the raspberry has no connection to wifi when detecting, you can skip this step. To receive email notifications when an Asian hornet is detected, follow these steps:

   - **Create a Gmail Account**: 
   - Create an account for your hornet detector. You can use an existing email or create a new one for safety and to avoid spam.

   - **Enable Two-Factor Authentication (2FA)**: 
   - Activate 2FA for your Gmail account to enhance security.

   - **Generate an App Password**: 
   - Create an [app password](https://support.google.com/mail/answer/185833?hl=en#:~:text=in%20or%20out-,Sign%20in%20with%20app%20passwords,-Sign%20in%20with) for your account. This password will be used instead of your regular email password.

   - **Configure Email Credentials**: 
   - Add your email address and app password to your `.bashrc` file:
   ```bash
   export EMAIL_USER="your_email@gmail.com"
   export EMAIL_PASS="your_app_password"
   ```

   - **Apply Changes**: 
   - Run the following command to apply the changes:
   ```bash
   source ~/.bashrc
   ```

### Important Notes:
- Ensure that you store your email credentials securely. Using environment variables, as shown above, is a good practice.
- The email will be sent when a Vespa velutina (vvel) is detected.

## Usage Guide

For the setup of the raspberry and camera module 3 check the official [documentation](https://www.raspberrypi.com/documentation/accessories/camera.html).

### Starting the Application
1. Open a terminal window
2. Type `./start_vespcv` and press Enter
3. The application window will open automatically

### Understanding the Interface
The application window is divided into several sections:

1. **Top Bar**
   - **START** (Green button): Starts the hornet detection
   - **STOP** (Orange button): Pauses the detection
   - **MAIL** (Gray/Blue button): Toggles email alerts for hornet detections
   - **GPIO** (Gray button): Controls the LED indicator (mockup for hornet trap or electric harp)
   - **LED Indicator** (●): Shows the current status of the detection system

2. **Main Screen**
   - **Left Panel**:
     - Shows the latest captured image with detection results
     - Detection chart displaying Asian hornet activity (red bars) and other insects (gray bars) over time
   - **Right Panel**:
     - Recent detections (click any image to save it to your desktop)
     - Detection log showing detections and system activity

### Using the System

1. **Starting Detection**
   - Detection starts automatically when the application launches
   - The captured image will appear on the left side
   - The system will automatically scan for hornets

2. **Email Alerts**
   - Click the **MAIL** button to enable email notifications
   - When enabled, you'll receive an email when the first Asian hornet is detected (requires internet connection and email configuration)
   - The MAIL button turns blue when email alerts are active

3. **Saving Detections**
   - When a hornet is detected, the image appears in the "Recent Detections" panel
   - Click any detection image to save it to your desktop (requires internet connection)
   - Images are automatically saved with date and time information in the `vespcv/data/images` folder

4. **Stopping the System**
   - Click the orange **STOP** button to pause detection
   - To close the application, click the X in the top-right corner

5. **Continuing Detection**
   - Click the green **START** button to resume detection after stopping

### Tips for Best Results
- Ensure the camera has a clear view of the area you want to monitor
- Keep the camera lens clean and free from obstructions
- Position the camera in a well-lit area for better detection

## Using Your Raspberry Pi Remotely

You can control and view your Raspberry Pi from another computer, tablet, or phone using **Raspberry Pi Connect**. This makes it easy to set up and monitor your hornet detector, even if you’re not near the device.

- **Raspberry Pi Connect**:  
  [Official Guide: How to use Raspberry Pi Connect](https://www.raspberrypi.com/documentation/computers/remote-access.html#raspberry-pi-connect)

If you’ve never used a Raspberry Pi before, check out these beginner-friendly guides:

- [Getting Started with Raspberry Pi](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [How to Set Up Your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up)
- [How to Connect a Camera to Raspberry Pi](https://www.raspberrypi.com/documentation/accessories/camera.html)

### Troubleshooting
If you encounter any issues:
1. Check that the camera is properly connected
2. Ensure the system has a stable internet connection for email alerts
3. If you have problems, you can also check the log files in the data/logs/ folder for more details.


## License
This project is licensed under the GPL Version 3. See the [LICENSE](LICENSE) file for details.

## Additional Resources
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/): Official documentation for Raspberry Pi.
- [YOLOv11 Documentation](https://docs.ultralytics.com/): Documentation for the YOLOv11 model.
- [OpenCV Documentation](https://docs.opencv.org/): Documentation for OpenCV, the library used for image processing.
- [Python Documentation](https://docs.python.org/3/): Official Python documentation for reference on Python programming.
- [waarnemingen.nl](https://waarneming.nl/): An official platform for reporting sightings of Asian hornets, allowing users to submit images and additional information to aid in monitoring and controlling hornet populations. 




