# vespCV - Asian Hornet Detection System

## Overview
The vespCV project is dedicated to creating an automated detection system for the invasive Asian hornet (Vespa velutina). This system utilizes computer vision technology to equip beekeepers, volunteers reporting hornet sightings to 'waarnemingen.nl', and researchers with a dependable tool for monitoring and managing hornet populations effectively.

## Table of Contents
- [Introduction](#introduction)
- [Installation Instructions](#installation-instructions)
- [Usage Guide](#usage-guide)
- [Using Your Raspberry Pi Remotely](#using-your-raspberry-pi-remotely)
- [Advanced configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Additional Resources](#additional-resources)

## Introduction
In recent years, the invasive Asian hornet (Vespa velutina) has posed a significant threat to honeybee populations and, consequently, to our ecosystems and agriculture. Background information on the problems and solutions related to this invasive exotic species can be found in the [wiki](https://github.com/vespCV/vespcv/wiki/Vespa-Computer-Vision). The `vespCV` project aims to develop an open-source non-profit automated detection system that empowers beekeepers, volunteers, and researchers to combat this growing challenge effectively.

### Problem Statement
The Asian hornet primarily preys on honeybees, which can lead to a decline in pollination performance, negatively impacting biodiversity and fruit cultivation. A single colony requires more than 11 kg of insect biomass annually. While honeybees are the most frequently predated species, wild pollinators and decomposers are also on their menu, along with nectar, which makes the Asian hornet also a nectar competitor.

### Solution Overview
Beekeepers, Asian hornet controlers, and researchers need a reliable, easy-to-use way to spot these hornets early. `vespCV` uses a Raspberry Pi 4 and a camera to automatically spot Asian hornets. It takes pictures, checks them with a computer vision model (YOLOv11s), and alerts you if an Asian hornet is found.

## Installation Instructions

### Hardware Requirements
- [**Raspberry Pi4 B**](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/?variant=raspberry-pi-4-model-b-8gb) (An 8GB and 4GB versions were used for this project) or a [**Raspberry Pi5**](https://www.raspberrypi.com/products/raspberry-pi-5/) (8GB)
- **Power Supply**: Ensure you have a suitable power supply for the Raspberry Pi. For edge detection in the field you can use a Raspberry Pi 4 with a 5V 3A powerbank. (The Raspberry Pi5 needs 5V 5A.)
- **Micro SD Card**: A 32GB card was used for this project.
- **Micro SD Card Reader**: Needed to flash the OS onto the micro SD card.
- **Camera**: 
  - **Raspberry Camera Module 3** or 
  - **Arducam IMX519 16MP Autofocus Camera Module** (a Camera module 2 will probably also work).
- **Camera Mount and Protector** (optional): To secure the camera in place.
- [**Bait lure**](https://www.rbka.org.uk/index.php/asian-hornet/traps-and-lures) : To attract hornets.

### Installing Raspberry Pi OS
1. Install Raspberry Pi OS Bookworm.
   - Use Raspberry Pi Imager to install Bookworm (64-bit) on your SD card. Select:
     - **Raspberry Pi Model**: Raspberry Pi 4 or Raspberry Pi 5
     - **Operating System**: Raspberry Pi OS (64-bit)
     - **Edit settings to preconfigure**:
       - **hostname**: pi
       - **username**: vcv
       - **password**: `choose-a-save-password`
       - Configure other options according to your Wi-Fi and time zone settings.
   - Detailed information can be found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html).
   - Connect a keyboard and monitor to the Raspberry Pi, or alternatively, or use [Raspberry Pi Connect](https://www.raspberrypi.com/documentation/services/connect.html) for remote access.
      Quick reference for using Raspberry Pi Connect:
      ```bash
      sudo apt install rpi-connect
      rpi-connect on
      rpi-connect signin
      # When the verification URL appears, copy and paste it into your browser, then sign in using your Raspberry Pi ID ```

2. Clone the repository:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   git clone https://github.com/vespCV/vespcv.git
   cd vespcv
   ```

3. Set up the virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Create a launch script named `start_vespcv`:
   ```bash
   nano /home/vcv/start_vespcv
   ```
   Copy and paste these lines into the file:
   ```bash
   #!/bin/bash

   # Change to the vespCV directory
   cd /home/vcv/vespcv

   # Activate the virtual environment
   source venv/bin/activate

   # Set display for GUI
   export DISPLAY=:0

   # Add the project root to PYTHONPATH
   export PYTHONPATH=/home/vcv/vespcv:$PYTHONPATH

   # Start the application using the virtual environment's Python
   /home/vcv/vespcv/venv/bin/python src/core/main.py
   ```
   Save the file by pressing:
   - `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

5. Make the script executable:
   ```bash
   chmod +x /home/vcv/start_vespcv
   ```

6. **Email Configuration (Optional)**:
   If you don't want email alerts, or if the Raspberry Pi has no connection to Wi-Fi when detecting, you can skip this step. To receive email notifications when an Asian hornet is detected, follow these steps:
   - **Create a Gmail Account**: Create an account for your hornet detector. You can use an existing email or create a new one for safety and to avoid spam.
   - **Enable Two-Factor Authentication (2FA)**: Activate 2FA for your Gmail account to enhance security.
   - **Generate an App Password**: Create an [app password](https://support.google.com/mail/answer/185833?hl=en#:~:text=in%20or%20out-,Sign%20in%20with%20app%20passwords,-Sign%20in%20with) for your account. This password will be used instead of your regular email password.
   - **Configure Email Credentials**: To receive email notifications when an Asian hornet is detected, you need to set up your email credentials. Follow these steps:
     - **Create a new file** in your home directory to store your email credentials:
        ```bash
        nano ~/.vespcv_credentials
        ```
     - **Add your email address and app password** to the file. Replace `your_email@gmail.com` and `your_app_password` with your actual email and the app password you generated:
        ```bash
        export EMAIL_USER="your_email@gmail.com"
        export EMAIL_PASS="your_app_password"
        ```
     - **Save the file** by pressing:
        - `Ctrl + X` to exit
        - Press `Y` to confirm changes
        - Press `Enter` to save
    - **Set File Permissions**:
      - To ensure that only you can read this file, set its permissions with the following command:
      ```bash
      chmod 600 ~/.vespcv_credentials
      ```
    - This command restricts access so that only the file owner can read and write it.
    - **Adjust Config**:
      - To enable the mail function by default, set `mail_alert_enabled` to `true` in the configuration file.

**Important**: Always store your email credentials securely. Avoid pushing this file to version control to protect your sensitive information. It's advisable to create a separate Gmail account specifically for the vespCV detector to enhance security and privacy.

7. **Install Arducam (skip this step if you have a Camera Module 3)**
   Follow [SOFTWARE GUIDE for IMX519 Autofocus Camera](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/16MP-IMX519/#supported-platforms-and-os) to install and test the driver en software.

8. **Set up autostart with GUI (optional)**:
   ```bash
   # Open the crontab editor
   crontab -e
   ```
   Choose option 1 and add this line to start the application at boot:
   ```bash
   @reboot sleep 30 && /home/vcv/start_vespcv >> /home/vcv/vespcv/data/logs/startup.log 2>&1
   ```
   The `sleep 30` ensures the system is fully booted before starting the application.

## Usage Guide

For the setup of the Raspberry Pi and camera module 3 check the official [documentation](https://www.raspberrypi.com/documentation/accessories/camera.html).

### Starting the Application
1. Open a terminal window (or `cd ~` to go back to your home directory)
2. Type `./start_vespcv` and press Enter
3. The application window will open automatically

![Start Screen](doc/images/StartScreen.png)

### Understanding the Interface

The application interface consists of the following sections:

1. **Top Bar**
   - **`START`** (Green button): Re-starts the hornet detection (only needed after pressing stop to continue)
   - **`STOP`** (Orange button): Pauses the detection
   - **`MAIL`** (Gray/Blue button): Toggles email alert for Asian hornet detection
   - **`GPIO`** (Gray/Red button): Controls external hardware like a trap or deterrent device (e.g., electric harp – placeholder functionality)

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
   - This function requires an internet connection and email configuration on the Raspberry Pi
   - Click the **MAIL** button to enable email notifications. When activated, the button will turn blue, and you will receive an email when the first Asian hornet is detected
   - Once the email is sent, the button will revert to gray

3. **Saving Detections**
   - When a hornet is detected, the image appears in the "Gedetecteerde Aziatische hoornaars" panel
   - Click any detection image to save it to the desktop of the Raspberry Pi
   - Images are automatically saved with date and time information in the `vespcv/data/images` folder

4. **Stopping the System**
   - Click the orange **STOP** button to pause detection
   - To close the application, click the X in the top-right corner

5. **Continuing Detection**
   - Click the green **START** button to resume detection after stopping

6. **Test the system**
   - For testing purposes, you can use the [insect slider](test/InsectSlider.m4v) to simulate different insect detections. Play the video on your computer monitor or smartphone in front of the camera as a mockup for real insects. This setup allows you to evaluate the system's response to various scenarios and ensures accurate hornet detection.

7. **Make space on SD**
   - The saved images, log files, and YOLO training files can be deleted all at once by removing the `data` folder.
   - When you restart the application, these folders will be created automatically

### Tips for Best Results
- Ensure the camera has a clear view of the area you want to monitor
- Keep the camera lens clean and free from obstructions
- Position the camera in a well-lit area for better detection

![Detections](doc/images/Detections.png)

## Using Your Raspberry Pi Remotely

You can control and view your Raspberry Pi from another computer, tablet, or phone using **Raspberry Pi Connect**. This makes it easy to set up and monitor your hornet detector, even if you're not near the device. However, this feature only works if the Raspberry Pi has access to a Wi-Fi network.

- **Raspberry Pi Connect**:  
  [Official Guide: How to use Raspberry Pi Connect](https://www.raspberrypi.com/documentation/computers/remote-access.html#raspberry-pi-connect)

If you've never used a Raspberry Pi before, check out these beginner-friendly guides:

- [Getting Started with Raspberry Pi](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [How to Set Up Your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up)
- [How to Connect a Camera to Raspberry Pi](https://www.raspberrypi.com/documentation/accessories/camera.html)

## Advanced Configuration

The system can be customized through the `config.yaml` file. Here are the main settings you can adjust:

### Detection Settings
- **Confidence Threshold** (default: 0.80)
  - Higher values (closer to 1.0) mean more certain detections
  - Lower values might catch more hornets but could include false positives
  - Recommended range: 0.80-0.90

### Camera Settings
- **Lens Position** (default: 1)
  - 0: Far distance (approximately 3 meters)
  - 1: Medium distance (approximately 1 meter)
  - 10: Close-up (approximately 10 centimeters)
  - To test lens position: `libcamera-still -t 0 --autofocus-mode continuous --info-text "%lp"`

### Timing Settings
- **Capture Interval** (default: 15 seconds)
  - How often the camera takes a new picture
  - Lower values mean more frequent checks but higher resource usage
  - Recommended range: 10-30 seconds

- **Chart Interval** (default: 15 minutes)
  - How detections are grouped in the activity chart
  - Affects how the detection history is displayed
  - Recommended range: 10-30 minutes

### GPIO Settings
- **GPIO Pin** (default: 21)
  - GPIO pin number for the LED or hardware connected to the Raspberry
  - Only change if you've connected the LED/hardware to a different pin

- **GPIO Duration** (default: 3 seconds)
  - How long the LED stays on after a detection of a Vespa velutina
  - Adjust based on your visibility needs

- **GPIO Enables** (default: false)
   - If the GPIO pin is activated after detection of a Vespa velutina

### Troubleshooting

If you encounter any issues, follow these steps:

1. **General Checks**:
   - Check that the camera is properly connected
   - Ensure the system has a stable internet connection for email alerts
   - If you have problems, check the log files in the `data/logs/` folder for more details

### Camera Issues
- **Camera not detected**: 
  - Ensure the camera is properly connected
  - Run `sudo raspi-config` and enable the camera interface
  - Check the camera function with
    ```bash
    libcamera-still -t 5000 # if you have a screen
    libcamera-jpeg -o test.jpg # check if a jpg is created
    ```
  - Reboot the Raspberry Pi.

### Model Detection Issues
- **Low detection accuracy**:
  - Check if the camera is properly focused.
  - Ensure adequate lighting.
  - Adjust confidence thresholds in the `config.yaml` if needed.

- **Model loading errors**:
  - Verify the model file (`best.pt`) is in the correct directory.
  - Check if the model file is not corrupted.
  - Ensure sufficient RAM is available (at least 4GB recommended).
  
  
### Network Issues
- **SSH connection problems**:
  - Verify the Raspberry Pi is on the same network.
  - Check if SSH is enabled:
    ```bash
    sudo systemctl status ssh
    ```
  - Verify that the IP address has not changed by using the command `hostname -I` or by running `ifconfig`.

### Raspberry Pi Connect Issues
- **Raspberry Pi does not reconnect after a prolonged period of inactivity with Raspberry Pi Connect**
   - Check the Raspberry Pi's IP address using the command `hostname -I` or by running `ifconfig`.
   - Verify its connection to Wi-Fi by using the command: `ping <IP-address>`.
   - SSH into the Raspberry Pi using: `ssh pi@<IP-address>`.
   - Then execute the following commands to reset the connection:

### GPIO Issues
- **GPIO Test Script for Connected Hardware**:
  - The script uses the `config.yaml` file to determine which GPIO pin to test. Ensure you have connected to pin 21 and ground, or change the default pin 21 to the pin you have connected in the `config.yaml`.
  - To use the `GPIO_test.py` file for testing the GPIO functionality on your Raspberry Pi, run the following command:
    ```bash
    export PYTHONPATH=$PYTHONPATH:/home/vcv/vespcv/src
    python test/GPIO_test.py
    ```

## License
This project is licensed under the GPL Version 3. See the [LICENSE](LICENSE) file for details.

## Additional Resources
### Vespa velutina (Yellow-Legged Hornet or Asian Hornet)
A comprehensive reference list can be found in this repository's GitHub wiki, which includes:
- Websites providing information on Asian hornets and guidance on what to do if you encounter one or discover a nest.
- Scientific papers covering:
  - [Invasion](https://github.com/vespCV/vespcv/wiki/invastion)
  - [Impact](https://github.com/vespCV/vespcv/wiki/impact)
  - [Detection](https://github.com/vespCV/vespcv/wiki/detect)
  - [Control](https://github.com/vespCV/vespcv/wiki/control)
### Edge Device Computer Vision
You can also find links related to edge computer vision, including:
- Raspberry Pi documentation
- Ultralytics YOLO documentation


