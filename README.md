# vespCV - Asian Hornet Detection System

## Introduction
In recent years, the invasive Asian hornet (Vespa velutina) has posed a significant threat to honeybee populations and, consequently, to our ecosystems and agriculture. The `vespCV` project aims to develop an innovative, automated detection system that empowers beekeepers, volunteers, and researchers to combat this growing challenge effectively.

### Problem Statement
The Asian hornet is not only a predator of honeybees but also disrupts the delicate balance of our ecosystems. Early detection is crucial for effective control, yet current methods are often manual, time-consuming, and prone to human error. This gap in monitoring creates a pressing need for a reliable, user-friendly solution.

### Solution Overview
The `vespCV` project leverages cutting-edge computer vision technology to create a robust detection system that operates on a Raspberry Pi 4. Utilizing the YOLOv11s model, our system processes real-time camera input to identify and log the presence of Asian hornets, providing immediate alerts and actionable insights.

## Dependencies
The following external libraries are required for the `vespCV` project:

- `ultralytics==8.3.137`
- `opencv-python==4.11.0.86`
- `numpy==2.2.5`
- `pandas==2.2.3`
- `gpiozero==1.6.2`
- `torch==2.7.0`  # Ensure this is the correct version for your Raspberry Pi

## Installation Instructions

### Step 1: Install Raspberry Pi OS Bookworm
To run the `vespCV` project, you need to install Raspberry Pi OS Bookworm on your Raspberry Pi. Follow these steps:

1. **Download Raspberry Pi Imager** from the official website: [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. **Install the Imager** on your computer.
3. **Open the Imager**, select the Raspberry Pi OS version (choose "Raspberry Pi OS (64-bit)" for Bookworm), and follow the prompts to flash it onto your SD card.
4. **Insert the SD card** into your Raspberry Pi and power it on. Complete the initial setup and configuration.

For detailed instructions, refer to this guide: [Install Raspberry Pi OS](https://raspberrytips.com/install-raspbian-raspberry-pi/).

### Step 2: Clone the Repository
```bash
git clone https://github.com/vespCV/vespcv.git
cd vespcv
```

### Step 3: Set Up the Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure the System
- Edit the `config/config.yaml` file to set your desired parameters.

## Usage Examples

1. **Run the Application**:
   - You can start the application using the provided shell script. First, ensure the script is executable:
     ```bash
     chmod +x ~/start_vespcv
     ```
   - Then, run the script:
     ```bash
     ./start_vespcv
     ```

2. **View Detection Results**:
   - The GUI will display real-time camera feed and detection results.

3. **Check Logs**:
   - Logs can be found in the `data/logs/` directory for monitoring system performance and errors.

## License
Public License (GPL) Version 3
This license allows users to freely use, modify, and distribute the software, provided that all copies and derivative works are also licensed under the same terms. For more details, please refer to the full license text.




