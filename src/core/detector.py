"""
Core detection module for the vespCV application.
Handles YOLO model loading, image capture, and object detection.
"""

import os
import time
import threading

import cv2
from ultralytics import YOLO

from src.utils.detection_utils import capture_image
from src.core.logger import logger

class DetectionController:
    def __init__(self, result_callback):
        """Initialize the detection controller.
        
        Args:
            result_callback: Function to call with detection results
        """
        self._thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.result_callback = result_callback

        # Load config and model
        self.config = self._load_config()
        self.model = self._create_model()

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

    def is_running(self):
        """Check if detection is currently running."""
        return self._thread is not None and self._thread.is_alive() and not self._pause_event.is_set()

    def _detection_loop(self):
        """Main detection loop."""
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue

            try:
                # Capture and process image
                result = self._process_single_frame()
                if result:
                    self.result_callback(result)
            except Exception as e:
                logger.error("Error in detection loop: %s", e)

            time.sleep(self.config['capture_interval'])

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

            # Save annotated image
            annotated_path = self._save_annotated_image(img, results)
            
            return {
                "image_path": annotated_path,
                "detection": detections
            }

        except Exception as e:
            logger.error("Error processing frame: %s", e)
            return None

    def _process_detections(self, results, img):
        """Process detection results and return detection info."""
        detected_classes = {}
        class_3_detected = False
        max_conf = 0.0

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = result[:6]
            if conf > self.config['conf_threshold']:
                # Draw bounding box
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                
                # Get class info
                class_id = int(cls)
                class_name = self.config['class_names'][class_id]
                detected_classes[class_id] = detected_classes.get(class_id, 0) + 1
                
                # Add label
                label = f"{class_name} {conf:.2f}"
                cv2.putText(img, label, (int(x1), int(y1) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Track class 3 and max confidence
                if class_id == 3:
                    class_3_detected = True
                max_conf = max(max_conf, conf)

        # Determine final class and confidence
        if detected_classes:
            if class_3_detected:
                final_class = "vvel"
            else:
                most_detected = max(detected_classes.items(), key=lambda x: x[1])
                final_class = self.config['class_names'][most_detected[0]]
            confidence = f"{max_conf:.2f}"
        else:
            final_class = "no_detection"
            confidence = "0.00"

        return {
            "class": final_class,
            "confidence": confidence,
            "timestamp": time.strftime("%Y%m%d-%H%M%S")
        }

    def _save_annotated_image(self, img, results):
        """Save the annotated image and return its path."""
        try:
            # Create filename
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"image_after_inference_{timestamp}.jpg"
            output_path = os.path.join(self.config['images_folder'], filename)
            
            # Save image
            cv2.imwrite(output_path, img)
            logger.debug("Saved annotated image: %s", output_path)
            
            return output_path
        except Exception as e:
            logger.error("Failed to save annotated image: %s", e)
            return None

    def shutdown(self):
        """Shutdown the detection controller."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        logger.info("Detection controller shut down")
