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

from src.utils.detection_utils import capture_image
from src.utils.image_utils import save_annotated_image
from src.core.logger import start_temperature_logging, logger, configure_logger, get_cpu_temperature

def load_config(config_path='config/config.yaml'):
    """Load the configuration from the specified YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as e:
        logger.error("Error: '%s' file not found.", config_path)
        raise e
    except yaml.YAMLError as e:
        logger.error("Error: Failed to parse the YAML config file.")
        raise e

    if 'model_path' not in config:
        raise KeyError("Error: 'model_path' key is missing in the config file.")
    
    if 'class_names' not in config:
        raise KeyError("Error: 'class_names' key is missing in the config file.")

    return config

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
        print(f"Attempting to save image to: {image_path}")  # Debug print
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

            # Check for class detection with high confidence
            for result in results.boxes.data.tolist():  # Each detection in format [x1, y1, x2, y2, conf, class]
                x1, y1, x2, y2, conf, cls = result[:6]
                if conf > config.get('conf_threshold', 0.8):  # Use threshold from config
                    # Draw the bounding box
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  # Green box

                    # Get the class name from the config
                    class_name = config['class_names'][int(cls)]  # Assuming cls is an index

                    # Optionally, add a label with class name and confidence
                    label = f"Class: {class_name}, Conf: {conf:.2f}"
                    cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Format the filename with class name and confidence score
                    confidence_score = f"{conf:.2f}"  # Format confidence to two decimal places
                    timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format time and date
                    new_image_name = f"{class_name}-{confidence_score}-{timestamp}.jpg"  # Use class name
                    new_image_path = os.path.join('data/images', new_image_name)

                    # Save the full image with the new filename
                    cv2.imwrite(new_image_path, img)  # Save the full image
                    print(f"Saved image: {new_image_path}")  # Debug print

        except Exception as e:
            logger.error("Error during inference: %s", e)

        time.sleep(config['capture_interval'])

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
