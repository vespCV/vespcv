"""
This file is the main file for the detector.
It loads the configuration, creates the model, and runs the inference.
"""

from ultralytics import YOLO
import yaml
import time
import os
import cv2 # OpenCV
import subprocess
import threading

from src.utils.detection_utils import capture_image
from src.utils.image_utils import save_annotated_image
from src.core.logger import start_temperature_logging, logger, configure_logger, get_cpu_temperature
from src.core.config_loader import load_config



def create_model(model_path):
    """Load the YOLO model from the given model path"""
    try:
        model = YOLO(model_path)
    except Exception as e:
        logger.error("Failed to load YOLO model: %s", e)
        raise e
    return model

def perform_inference(model, image_path):
    """Run inference, returns raw results"""
    # Run YOLO inference on the image
    results = model(image_path)
    return results  # Return the raw results

def capture_image():
    """Capture an image using libcamera-still and save it to the configured path.
    
    Returns:
        str: Path to the captured image
    """
    try:
        config = load_config()  # Loads the config dict
        images_folder = config.get('images_folder', '/home/vcv/vespcv/data/images')  # Update to your path
        image_path = os.path.join(images_folder, "image_for_detection.jpg")
        logger.debug(f"Attempting to save image to: {image_path}")
        subprocess.run([ 
            "libcamera-still",
            "-o", image_path,  # Save the image_for_detection.jpg
            "--width", "4656",
            "--height", "3496"
        ])
        return image_path
    except Exception as e:
        print(f"Error capturing image: {e}")
        raise e

def inference_loop(model, config):
    """Main loop for continuous inference cycles."""
    while True:
        try:
            image_path = capture_image()  # Ensure this function handles errors
            print(f"Captured image path: {image_path}")  # Debug print

            # Load the full image (no magnification)
            img = cv2.imread(image_path)

            # Apply YOLO inference to the full image
            results = model(img)[0]

            # Initialize variables to track detections
            detected_classes = {}  # Dictionary to count occurrences of each class
            class_3_detected = False  # Flag for class 3 detection

            # Check for class detection with high confidence
            for result in results.boxes.data.tolist():  # Each detection in format [x1, y1, x2, y2, conf, class]
                x1, y1, x2, y2, conf, cls = result[:6]
                if conf > config.get('conf_threshold', 0.8):  # Use threshold from config
                    # Draw the bounding box
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  # Green box

                    # Get the class name from the config
                    class_name = config['class_names'][int(cls)]  # Assuming cls is an index
                    detected_classes[int(cls)] = detected_classes.get(int(cls), 0) + 1  # Count occurrences

                    # Optionally, add a label with class name and confidence
                    label = f"Class: {class_name}, Conf: {conf:.2f}"
                    cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Check if class 3 is detected
                    if int(cls) == 3:
                        class_3_detected = True

            # Determine the class name for the filename
            if class_3_detected:
                final_class_name = "vvel"
            else:
                # Find the most detected species
                most_detected_class = max(detected_classes, key=detected_classes.get, default=None)
                if most_detected_class is not None:
                    final_class_name = config['class_names'][most_detected_class]  # Use the name of the most detected class
                else:
                    print("No classes detected; image not saved.")  # Debug print
                    continue  # Skip saving the image if no classes are detected

            # Format the filename with the determined class name and confidence score
            confidence_score = f"{conf:.2f}"  # Use the last detected confidence score
            timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format time and date
            new_image_name = f"{final_class_name}-{confidence_score}-{timestamp}.jpg"  # Use final class name
            new_image_path = os.path.join('data/images', new_image_name)

            # Save the full image with the new filename
            cv2.imwrite(new_image_path, img)  # Save the full image
            print(f"Saved image: {new_image_path}")  # Debug print

            # Save the image after inference with bounding boxes
            after_inference_image_path = os.path.join('data/images', 'image_after_inference.jpg')
            cv2.imwrite(after_inference_image_path, img)  # Save the image with bounding boxes
            print(f"Saved image after inference: {after_inference_image_path}")  # Debug print

        except Exception as e:
            logger.error("Error during inference: %s", e)

        time.sleep(config['capture_interval'])

class DetectionController:
    def __init__(self, result_callback):
        self._thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.result_callback = result_callback  # Function to send results to GUI

        # Load config and model once
        self.config = load_config()
        self.model = create_model(self.config['model_path'])

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._pause_event.clear()
            self._thread = threading.Thread(target=self._detection_loop, daemon=True)
            self._thread.start()
        else:
            self._pause_event.clear()  # Resume if paused

    def stop(self):
        self._pause_event.set()  # Pause detection

    def is_running(self):
        return self._thread is not None and self._thread.is_alive() and not self._pause_event.is_set()

    def _detection_loop(self):
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue

            try:
                # 1. Capture image
                image_path = capture_image()
                img = cv2.imread(image_path)

                # 2. Run YOLO inference
                results = self.model(img)[0]

                # 3. Process results
                detected_classes = {}
                class_3_detected = False
                conf = 0.0  # Default confidence

                for result in results.boxes.data.tolist():
                    x1, y1, x2, y2, conf, cls = result[:6]
                    if conf > self.config.get('conf_threshold', 0.8):
                        class_name = self.config['class_names'][int(cls)]
                        detected_classes[int(cls)] = detected_classes.get(int(cls), 0) + 1
                        if int(cls) == 3:
                            class_3_detected = True

                # 4. Determine filename and save image
                if class_3_detected:
                    final_class_name = "vvel"
                else:
                    most_detected_class = max(detected_classes, key=detected_classes.get, default=None)
                    if most_detected_class is not None:
                        final_class_name = self.config['class_names'][most_detected_class]
                    else:
                        continue  # No detection, skip

                confidence_score = f"{conf:.2f}"
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                new_image_name = f"{final_class_name}-{confidence_score}-{timestamp}.jpg"
                new_image_path = os.path.join('data/images', new_image_name)
                cv2.imwrite(new_image_path, img)

                # Save image after inference (for live feed)
                after_inference_image_path = os.path.join('data/images', 'image_after_inference.jpg')
                cv2.imwrite(after_inference_image_path, img)

                # 5. Send result to GUI
                result = {
                    "image_path": after_inference_image_path,
                    "detection": {
                        "class": final_class_name,
                        "confidence": confidence_score,
                        "timestamp": timestamp
                    }
                }
                self.result_callback(result)

            except Exception as e:
                logger.error("Error during detection: %s", e)

            time.sleep(self.config['capture_interval'])

    def shutdown(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

def main():
    """Main function to run the detector."""
    start_temperature_logging()  # Start logging temperature
    try:
        config = load_config()
        configure_logger(config['log_file_path'])
        # Log CPU temperature at startup
        initial_temp = get_cpu_temperature()
        if initial_temp is not None:
            logger.info("Initial CPU Temperature: %.2f °C", initial_temp)
        model = create_model(config['model_path'])
        logger.info("Starting inference loop.")
        inference_loop(model, config)  # Start the inference loop
    except Exception as e:
        logger.critical("Critical error occurred: %s", e)
        exit(1)  # Exit if there is a critical error

if __name__ == '__main__':
    main()  # Call the main function
