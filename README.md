# vespCV - Asian Hornet Detection System

## Overview
The vespCV project aims to develop an automated detection system for the invasive Asian hornet (Vespa velutina). This system leverages computer vision technology to provide beekeepers and researchers with a reliable tool for monitoring and controlling hornet populations.

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
1. Install Raspberry Pi OS Bookworm.
2. Create a directory for the project:
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

## Usage Guide
To run the application, execute:
```bash
./start_vespcv
```
The GUI will display real-time camera feed and detection results.

## Directory Structure
The project is organized into several main directories, each serving a specific purpose:

- **`main.py`**: Entry point for the application, handling configuration loading and GUI initialization.
- **`src/`**: Core application code, including:
  - **`core/`**: Main detection logic and utilities.
  - **`gui/`**: GUI components built using Tkinter.
  - **`utils/`**: Helper functions for image processing and other utilities.
- **`config/`**: Configuration files in YAML format.
- **`models/`**: Stores trained model weights used for detection.
- **`tests/`**: Contains unit and integration tests.
- **`doc/`**: Documentation files, including the Product Requirements Document (PRD).
- **`data/`**: Stores generated data, including images and logs.

## License
This project is licensed under the GPL Version 3. See the [LICENSE](LICENSE) file for details.

## Additional Resources
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/): Official documentation for Raspberry Pi.
- [YOLOv11 Documentation](https://docs.ultralytics.com/): Documentation for the YOLOv11 model.
- [OpenCV Documentation](https://docs.opencv.org/): Documentation for OpenCV, the library used for image processing.
- [Python Documentation](https://docs.python.org/3/): Official Python documentation for reference on Python programming.
- [waarnemingen.nl](https://waarneming.nl/): An official platform for reporting sightings of Asian hornets, allowing users to submit images and additional information to aid in monitoring and controlling hornet populations. 




