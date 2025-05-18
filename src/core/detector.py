"""
This file is the main file for the detector.
It loads the configuration, creates the model, and runs the inference.
"""

from ultralytics import YOLO
import yaml
import time
import os
import cv2 # OpenCV

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

def inference_loop(model, config):
    """Main loop for continuous inference cycles."""
    while True:
        try:
            image_path = capture_image()  # Ensure this function handles errors

            raw_results = perform_inference(model, image_path)

            should_save = False
            if raw_results and raw_results[0].boxes is not None:
                for box in raw_results[0].boxes:
                    if box.conf[0] > config.get('conf_threshold', 0.8):
                        should_save = True
                        break

            if should_save:
                save_annotated_image(image_path, raw_results, config)

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
