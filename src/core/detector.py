"""
Core detection module for the vespCV application.
Handles YOLO model loading, image capture, and object detection.
"""

import os
import time
import threading
import subprocess

import cv2
from ultralytics import YOLO

from src.utils.detection_utils import capture_image, save_annotated_image, save_original_image, save_archived_image, save_main_detection_image
from src.core.logger import logger
from src.utils.gpio_controller import GPIOController

class DetectionController:
    def __init__(self, result_callback, led_controller=None):
        """Initialize the detection controller.
        
        Args:
            result_callback: Function to call with detection results
            led_controller: Optional LEDController instance. If None, creates a new one.
        """
        self._thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.result_callback = result_callback

        # Load config and model
        self.config = self._load_config()
        self.model = self._create_model()
        
        # Initialize LED controller
        self.led_controller = led_controller if led_controller is not None else GPIOController()

    def _load_config(self):
        """Load the configuration."""
        from src.core.config_loader import load_config
        return load_config()

    def _create_model(self):
        """Create and return the YOLO model."""
        try:
            model = YOLO(self.config['model_path'])
            logger.info("YOLO model loaded successfully")
            return model
        except Exception as e:
            logger.error("Failed to load YOLO model: %s", e)
            raise

    def start(self):
        """Start the detection process."""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._pause_event.clear()
            self._thread = threading.Thread(target=self._detection_loop, daemon=True)
            self._thread.start()
            logger.info("Detection started")
        else:
            self._pause_event.clear()
            logger.info("Detection resumed")

    def stop(self):
        """Stop the detection process."""
        self._pause_event.set()
        logger.info("Detection paused")
        self.led_controller.cleanup()

    def is_running(self):
        """Check if detection is currently running."""
        return self._thread is not None and self._thread.is_alive() and not self._pause_event.is_set()

    def _detection_loop(self):
        """Main detection loop."""
        last_detection_time = 0
        consecutive_errors = 0
        max_consecutive_errors = 10  # Reduced from 5 to trigger reboot sooner
        
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                if self._stop_event.wait(0.1):
                    break
                continue

            try:
                current_time = time.time()
                time_since_last = current_time - last_detection_time
                
                # Subtract x seconds from the configured capture interval
                adjusted_capture_interval = self.config['capture_interval'] - 3 # seconds to compensate for the time it takes to process the image    

                
                # Only proceed if enough time has passed since last detection
                if time_since_last >= adjusted_capture_interval:
                    # Capture and process image
                    result = self._process_single_frame()
                    if result:
                        self.result_callback(result)
                        last_detection_time = current_time
                        consecutive_errors = 0  # Reset error counter on success
                    else:
                        consecutive_errors += 1
                        logger.warning(f"Failed to process frame (consecutive errors: {consecutive_errors})")
                    
                    # Check if LED needs to be turned off
                    self.led_controller.check_and_turn_off()
                else:
                    # Sleep for a short time to prevent busy waiting
                    time.sleep(0.1)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in detection loop (consecutive errors: {consecutive_errors}): {e}")
                
                # If we have too many consecutive errors, trigger reboot
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(f"Too many consecutive errors ({consecutive_errors}), triggering system reboot...")
                    try:
                        # Schedule reboot in 1 minute to allow logging to complete
                        import subprocess
                        subprocess.run(['sudo', 'shutdown', '-r', '+1'], check=False)
                        logger.critical("System reboot scheduled in 1 minute")
                        # Exit the process to allow reboot to proceed
                        import sys
                        sys.exit(1)
                    except Exception as e:
                        logger.critical(f"Failed to schedule reboot: {e}")
                        # Force exit anyway
                        import sys
                        sys.exit(1)
                else:
                    # Sleep briefly on error to prevent tight error loops
                    time.sleep(2)

            # Check for stop event
            if self._stop_event.wait(0.1):
                break

    def _process_single_frame(self):
        """Process a single frame and return detection results."""
        try:
            # Capture image
            image_path = capture_image()
            if not image_path or not os.path.exists(image_path):
                logger.error("Failed to capture image")
                return None

            # Load image
            img = cv2.imread(image_path)
            if img is None:
                logger.error("Failed to load captured image")
                return None

            # Run inference
            results = self.model(img)[0]
            
            # Process detections
            detections = self._process_detections(results, img)
            if not detections:
                return None

            # Handle LED for valid detections
            if detections.get("class") == "vvel":
                self.led_controller.handle_detection()

            # Save ALL images when any detection is made (not just vvel)
            if detections.get("should_archive"):
                # Save original image with detection metadata and YOLO results
                original_path = save_original_image(self.config, detections, results)

                # Save annotated image for GUI
                annotated_path = save_annotated_image(img, results, self.config)
                
                # Save archived image with detection info in filename
                archive_path = save_archived_image(img, detections, self.config)
                
                # Save a copy in the main images folder for easy access
                main_image_path = save_main_detection_image(img, detections, self.config)
                
                logger.info(f"Detection saved: {detections['class']} (confidence: {detections['confidence']})")
                
                return {
                    "annotated_path": annotated_path,
                    "original_path": original_path,
                    "archive_path": archive_path,
                    "main_image_path": main_image_path,
                    "detection": detections
                }
            else:
                # No detection, just save annotated image for GUI
                annotated_path = save_annotated_image(img, results, self.config)
                return {
                    "annotated_path": annotated_path,
                    "detection": detections
                }

        except subprocess.SubprocessError as e:
            logger.error(f"Camera subprocess error: {e}")
            return None
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None

    def _process_detections(self, results, img):
        """Process detection results and return detection info."""
        detected_classes = {}
        class_3_detected = False
        class_3_conf = 0.0
        max_conf = 0.0
        max_conf_class = None
        all_detections = []

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = result[:6]
            if conf > self.config['conf_threshold']:
                class_id = int(cls)
                class_name = self.config['class_names'][class_id]
                detected_classes[class_id] = max(detected_classes.get(class_id, 0), conf)  # store max conf per class
                
                # Store all detections for logging
                all_detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'class_id': class_id
                })

                if class_id == 3 and conf > class_3_conf:
                    class_3_detected = True
                    class_3_conf = conf

                if conf > max_conf:
                    max_conf = conf
                    max_conf_class = class_id

                # Only draw bounding box and label if confidence is 0.6 or higher
                if conf >= 0.6:
                    # Draw bounding box
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 10)
                    
                    # Add label
                    label = f"{class_name} {conf:.2f}"
                    cv2.putText(img, label, (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 15.0, (0, 255, 0), 15)

        # Determine the primary detection class
        if class_3_detected:
            final_class = "vvel"
            confidence = f"{class_3_conf:.2f}"
        elif max_conf_class is not None:
            final_class = self.config['class_names'][max_conf_class]
            confidence = f"{max_conf:.2f}"
        else:
            final_class = "no_detection"
            confidence = "0.00"

        # Log all detections if any were found
        if all_detections:
            detection_summary = ", ".join([f"{d['class']}({d['confidence']:.2f})" for d in all_detections])
            logger.info(f"Detections found: {detection_summary}")

        return {
            "class": final_class,
            "confidence": confidence,
            "timestamp": time.strftime("%Y%m%d-%H%M%S"),
            "should_archive": final_class != "no_detection",
            "all_detections": all_detections  # Include all detections for reference
        }

    def shutdown(self):
        """Shutdown the detection controller."""
        try:
            logger.info("Starting detector shutdown...")
            
            # Set stop event to stop the detection loop
            self._stop_event.set()
            self._pause_event.set()  # Also set pause event to ensure loop exits
            
            # Wait for thread to finish with timeout
            if self._thread and self._thread.is_alive():
                logger.info("Waiting for detection thread to finish...")
                
                # Try graceful shutdown first
                self._thread.join(timeout=3.0)  # Increased timeout to 3 seconds
                
                if self._thread.is_alive():
                    logger.warning("Detection thread did not stop gracefully, forcing termination...")
                    # Force cleanup by setting events again
                    self._stop_event.set()
                    self._pause_event.set()
                    
                    # Wait a bit more
                    self._thread.join(timeout=2.0)
                    
                    if self._thread.is_alive():
                        logger.error("Detection thread still alive after forced termination")
                    else:
                        logger.info("Detection thread terminated after forced cleanup")
                else:
                    logger.info("Detection thread stopped gracefully")
            
            # Add a small delay to ensure camera operations complete
            time.sleep(1.0)  # Increased delay for better cleanup
            
            logger.info("Detector shutdown complete")
        except Exception as e:
            logger.error(f"Error during detector shutdown: {e}")
            # Ensure events are set even if there's an error
            self._stop_event.set()
            self._pause_event.set()
