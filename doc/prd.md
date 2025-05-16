# Product Requirements Document: vespCV - Asian Hornet Detector
Version 0.3

## Table of Contents
1. [Introduction](#1-introduction)
2. [Goals](#2-goals)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Technical Requirements](#6-technical-requirements)
7. [Release Criteria](#7-release-criteria)
8. [Future Improvements](#8-future-improvements)
9. [Log Formats and Details](#9-log-formats-and-details)

## 1. Introduction

### 1.1 Purpose
This document outlines the functional and non-functional requirements for vespCV, an application designed to detect Asian hornets (Vespa velutina) using a Raspberry Pi 4, a Camera Module 3, and a YOLOv11s object detection model.

### 1.2 Target Audience
This document is intended for the development team, testers, and other stakeholders involved in the development of vespCV.

### 1.3 Context
The Asian hornet is an invasive species posing a threat to biodiversity and the honeybee population. Early detection is crucial for effective control. vespCV offers an automated solution for this detection.

### 1.4 Operation
Camera input → AI detection → storage/logging

## 2. Goals

### 2.1 Primary Goals (Proof of Concept)
- Real-time detection of Asian hornets in camera feeds
- Local deployment on a cost-effective Raspberry Pi 4
- Simple installation and configuration
- Storage of detection images and log records

### 2.2 Secondary Goals (User Application)
- User-friendly graphical interface (GUI) for monitoring and configuration
- Ability to export detection data
- Automation of application startup

## 3. User Stories

1. As a beekeeper, I want to place vespCV at my apiary so that I am warned early of the presence of Asian hornets, allowing me to take swift action.

2. As a volunteer monitoring invasive species, I want an affordable and easy-to-deploy solution to map the spread of the Asian hornet in my region.

3. As a researcher, I want access to logged detection data and images to analyze the behavior patterns of Asian hornets.

## 4. Functional Requirements

### 4.1 Detection
| ID | Requirement | Description |
|----|-------------|-------------|
| FR01 | Camera Processing | The application shall be able to process live video streams from the Raspberry Pi Camera Module 3. |
| FR02 | Model Usage | The application must use the YOLOv11s model to perform object detection on the video streams. |
| FR03 | Detection Accuracy | The application must accurately detect Asian hornets in the video streams. |
| FR04 | Detection Display | Upon detection, the application shall provide a bounding box and a label ("Asian hornet") for the detected object. |
| FR05 | Confidence Threshold | The application must use a threshold value (confidence score) to filter detections. This threshold value must be configurable. |

### 4.2 Storage
| ID | Requirement | Description |
|----|-------------|-------------|
| FR06 | Image Storage | Upon detection, the application shall save an image of the frame containing the detected hornet in the data/images/ directory. The filename must include the species, confidence score, and timestamp. |
| FR07 | Logging | The application shall log detection information (species, confidence score, timestamp, bounding box location) in a CSV file in the data/logs/ directory. |

### 4.3 Configuration
| ID | Requirement | Description |
|----|-------------|-------------|
| FR08 | Config Loading | The application must load configuration settings from files in the config/ directory. |
| FR09 | Configurable Parameters | The following parameters must be configurable:
- Detection threshold value (confidence score)
- Storage location for images
- Storage location for log files
- Any model-specific parameters |

### 4.4 User Interface (GUI - Optional)
| ID | Requirement | Description |
|----|-------------|-------------|
| FR10 | GUI Implementation | The application, if implemented, shall offer a graphical interface (GUI). |
| FR11 | Live Feed Display | The GUI must display a live feed from the camera with bounding boxes around detected Asian hornets. |
| FR12 | Configuration Interface | The GUI must allow modification of the configuration parameters (as mentioned in FR09). |
| FR13 | Detection Display | The GUI must display the 4 detections with the highest confidence from the current session (with image and log information). |

### 4.5 Autostart
| ID | Requirement | Description |
|----|-------------|-------------|
| FR14 | Boot Configuration | The application must be configurable to start automatically upon Raspberry Pi boot. |

### 4.6 Error Handling
| ID | Requirement | Description |
|----|-------------|-------------|
| FR15 | Error Logging | The application must log error messages (e.g., failed camera access or full storage medium) and make them visible (in GUI or CLI). |

## 5. Non-Functional Requirements

### 5.1 Performance
| ID | Requirement | Description |
|----|-------------|-------------|
| NFR01 | Real-time Detection | Detection must occur in near real-time (minimal delay between event and detection). |
| NFR02 | Resource Usage | The application must not excessively burden the Raspberry Pi 4 system resources (<70% CPU over a 5-minute average). |

### 5.2 Reliability
| ID | Requirement | Description |
|----|-------------|-------------|
| NFR03 | Stability | The application must run stably and minimize crashes. |
| NFR04 | Data Consistency | Logged data must be consistent and accurate. |

### 5.3 Usability
| ID | Requirement | Description |
|----|-------------|-------------|
| NFR05 | Installation | The application must be easy to install and configure, even for users with limited technical knowledge (especially basic configuration). Installation via SD card. |
| NFR06 | Interface Design | The GUI must be intuitive and easy to understand. |

### 5.4 Maintainability
| ID | Requirement | Description |
|----|-------------|-------------|
| NFR07 | Code Quality | The code must be structured and well-documented to facilitate future updates and maintenance. |

### 5.5 Scalability (Future)
| ID | Requirement | Description |
|----|-------------|-------------|
| NFR08 | Cloud Integration | The possibility of integration with cloud services or other platforms may be considered in the future. |

## 6. Technical Requirements

### 6.1 Platform
- Raspberry Pi 4 (4GB)

### 6.2 Operating System
- Raspberry Pi OS (bookworm)

### 6.3 Programming Language
- Python

### 6.4 Libraries
- Requirements as specified in requirements.txt
- OpenCV
- PyTorch (or another library for loading and executing the YOLO model)
- GUI libraries (such as Tkinter or PyQt if FR10-FR13 are implemented)

### 6.5 Hardware
- Raspberry Pi Camera Module 3

### 6.6 Model
- YOLOv11s (model weights optimized and ready in the models/ directory)

### 6.7 Development Environment
- Development via SSH using Cursor/VSCode

## 7. Release Criteria

1. All primary functional requirements (FR01-FR07 and FR14) are implemented and tested.
2. The application detects Asian hornets with a minimum accuracy of 99%. Accuracy will be measured by recording all observed insects (image and timestamp) in a test setup and subsequently analyzing them manually and comparing them to the application's detections.
3. The application runs stably on the Raspberry Pi 4 for 12 hours.
4. Basic documentation for installation and configuration is available.

## 8. Future Improvements (Backlog)

1. Implementation of the optional GUI (FR10-FR13)
2. Ability to send detection notifications (e.g., via email or another service)
3. Triggering of a connected mechanical defense or capture mechanism upon detection (such as an electrically operated harp)
4. Integration with GPS modules for geotagging detections
5. Support for training the model with new data
6. Implementation of more advanced analysis of detection patterns

## 9. Log Formats and Details

### 9.1 Format
- .csv (Comma Separated Values)

### 9.2 Content per Detection
- Species name
- Confidence score of the detection
- Timestamp of the detection (YYYY-MM-DD HH:MM:SS)
- Location of the bounding box (x_min, y_min, x_max, y_max) in the image
- Filename of the saved image

### 9.3 Extra Log Information
- **Temperature**: The ambient temperature, ideally measured by a sensor connected to the Raspberry Pi, at half-hourly intervals
- **Camera Status**: Any error messages or status updates from the camera (e.g., if the camera is not working correctly or has timed out)
- **Available Memory**: Regularly logging the available RAM memory on the Raspberry Pi can help in debugging performance issues
- **CPU Load**: Regularly logging the CPU load can also provide insight into the application's performance
- **Frame Rate**: If possible, log the frame rate of the processed video stream. This can help in assessing real-time performance