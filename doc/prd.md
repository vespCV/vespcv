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
The goal is to create a system specifically designed for the detection of Vespa velutina (Asian-/Yellowlegged hornets) in areas where this hornet is an invasive species. This detector aims to provide a solution to the increasing challenges posed by this hornet to the honeybee population due to its aggressive predation behavior. 

### 1.2 Target Audience
This document is intended for the development team, testers, and other stakeholders involved in the development of vespCV.

### 1.3 Context
In Europe, the Asian hornet is an invasive species posing a threat to the honeybee population. Effects on other insects and subsequent birds and pollination is not clear a decade after introduction of the first insect in France. Early detection is crucial for effective control. vespCV offers an automated solution for this detection. In the spring it can be a selective trap, not harming other insects such as the European hornet. In the summer it can aid the detection of workers that can subsequently be equiped with a microtransmitter to track and destruct the nest.

### 1.4 Operation
Camera input → AI detection → storage + logging
                            
                            → queen trap
                            
                            → catch hornet → transmitter
                            
                            → research

## 2. Goals

### 2.1 Main objective
- To develop and implement a robust and reliable computer vision system for the real-time detection of Vespa velutina.

### 2.2 Sub-objectives
- User-friendly system for beekeepers, Asian hornet controlers, citizens.
- Retrain with captured images to minimize false positives en improve detection accuracy under various environmental conditions.
- Provide a log file, trigger for action of a electronic harp, sending an email upon detection.
- Design a scalable system that can be applied in various contexts.
- Collect training data to assist system developers.


## 3. User Stories

1. As a beekeeper, I want to place vespCV at my apiary so that I am warned early of the presence of Asian hornets, and automatically activates a electric harp to protect the bees.

2. As a volunteer monitoring invasive species, I want to receive a almost realtime email with the captured image to send it to 'waarnemingen.nl'.

3. As a researcher, I want access to logged detection data and images to analyze the behavior patterns of Asian hornets.

## 4. Functional Requirements (FR)

### 4.1 Detection
| ID | Requirement | Description |
|----|-------------|-------------|
| FR01 | Camera Processing | The application shall be able to process captures images from the Raspberry Pi Camera Module 3. |
| FR02 | Model Usage | The application uses the YOLOv11s model to perform object detection on the captured images. |
| FR03 | Detection Accuracy | The application must accurately detect Asian hornets. |
| FR04 | Detection Display | Upon detection, the application shall provide a bounding box and a label ("vvel") for the detected object. Additionally, bees, European hornets, and wasps are included in the training set and can be detected. |
| FR05 | Confidence Threshold | The application must use a threshold value (confidence score) to filter detections. This threshold value must be configurable. |

### 4.2 Storage
| ID | Requirement | Description |
|----|-------------|-------------|
| FR06 | Image Storage | Upon detection, the application shall save an image of the frame containing the detected hornet in the data/images/ directory. The filename must include the species, confidence score, and date- and timestamp. |
| FR07 | Logging | The application shall log detection information of detected species, confidence score, timestamp, bounding box location (for retraining purposes), optional location data, system values (cpu temp, cpu usage) and errors in .log files in the data/logs/ directory. |

### 4.3 Configuration
| ID | Requirement | Description |
|----|-------------|-------------|
| FR08 | Config Loading | The application must load configuration settings from files in the config/ directory. |
| FR09 | Configurable Parameters | The following parameters must be configurable: - detection threshold value (confidence score), - email adres, - download location, - GPIO activation

### 4.4 User Interface
| ID | Requirement | Description |
|----|-------------|-------------|
| FR10 | GUI Implementation | The application, if implemented, shall offer a graphical interface (GUI). |
| FR11 | Most recent captured image | The GUI must display the latest captured and infered image with bounding boxes around detected species. |
| FR12 | Configuration Interface | The GUI must allow modification of the configuration parameters (as mentioned in FR09). |
| FR13 | Detection Display | The GUI must display the 4 detections with the highest confidence from the current session (with image and log information) and download option. |

### 4.5 Autostart and gracefull shutdown
| ID | Requirement | Description |
|----|-------------|-------------|
| FR14 | Boot Configuration | The application must be configurable to start automatically upon Raspberry Pi boot and stop with in button (for headless application). |

### 4.6 Error Handling
| ID | Requirement | Description |
|----|-------------|-------------|
| FR15 | Error Logging | The application must log error messages (e.g., failed camera access or full storage medium) and make them visible (in GUI or CLI). |

## 5. Non-Functional Requirements (NFR)

### 5.1 Performance
| ID | Requirement | Description |
|----|-------------|-------------|
| NFR01 | Real-time Detection | Detection must occur in near real-time (1 min delay between the event and detection is acceptable). |
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
| NFR08 | Cloud Integration | The possibility of integration with cloud services or other platforms could be considered in the future. |

## 6. Technical Requirements

### 6.1 Platform
- Raspberry Pi 4 or Raspberry Pi 5 with at least 4GB of RAM

### 6.2 Operating System
- Raspberry Pi OS (bookworm)

### 6.3 Programming Language
- Python

### 6.4 Libraries
- `ultralytics` for YOLO (You Only Look Once) model implementation (version 8.3.137)
- `opencv-python` for image processing (version 4.11.0.86)
- `numpy` for numerical operations (version 2.2.5)
- `pandas` for data manipulation and analysis (version 2.2.3)
- `gpiozero` for GPIO control (version 1.6.2)
- `torch` for deep learning framework (version 2.7.0)
- GUI libraries (such as Tkinter or PyQt if FR10-FR13 are implemented)

### 6.5 Hardware
- Raspberry Pi Camera Module 3

### 6.6 Model
- YOLOv11s (model weights optimized and ready in the models/ directory)

### 6.7 Development Environment
- Development via SSH using Cursor/VSCode.
- Raspberry Pi Connect for system testing.

## 7. Release Criteria

1. All primary functional requirements (FR01-FR07 and FR14) are implemented and tested.
2. The application detects Asian hornets with a minimum accuracy of 99%. Accuracy will be measured by recording all observed insects (image and timestamp) in a test setup and subsequently analyzing them manually and comparing them to the application's detections.
3. The application runs stably on the Raspberry Pi 4 for 12 hours.
4. Basic documentation for installation and configuration is available.

## 8. Future Improvements (Backlog)

1. Integration with GPS modules for geotagging detections
2. Sending JPG and TXT files to developers for monitoring and retraining purposes
3. Implementation of more advanced analysis of detection patterns (combination with sound)

## 9. Log Formats and Details

### 9.1 Format
- .log or .csv

### 9.2 Content per Detection
- Species name
- Confidence score of the detection
- Timestamp of the detection (YYYY-MM-DD HH:MM:SS)
- Location of the bounding box (x_min, y_min, x_max, y_max) in the image
- Filename of the saved image

### 9.3 Extra Log Information
- **Timestamp**: The date and time when the log entry was created, formatted as `YYYY-MM-DD HH:MM:SS,SSS` (where `SSS` represents milliseconds).
- **Log Level**: Indicates the severity or type of the log message (e.g., `INFO`, `ERROR`).
- **Message**: A descriptive message providing information about the application's state or actions taken.

### 9.4 Extra Log Information
- **Temperature**: The ambient temperature, ideally measured by a sensor connected to the Raspberry Pi, at half-hourly intervals
- **Camera Status**: Any error messages or status updates from the camera (e.g., if the camera is not working correctly or has timed out)
- **Available Memory**: Regularly logging the available RAM memory on the Raspberry Pi can help in debugging performance issues
- **CPU Load**: Regularly logging the CPU load can also provide insight into the application's performance
-**camera focus** if autofocus is used