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

def load_config(config_path='config/config.yaml'):
    """Load the configuration from the specified YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as e:
        print(f"Error: '{config_path}' file not found.")
        raise e
    except yaml.YAMLError as e:
        print("Error: Failed to parse the YAML config file.")
        raise e

    if 'model_path' not in config:
        raise KeyError("Error: 'model_path' key is missing in the config file.")

    return config

def create_model(model_path):
    """Load the YOLO model from the given model path"""
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error {e}: Failed to load YOLO model.")
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
            # Implement logging here
            print(f"Error: {e}")

        time.sleep(config['capture_interval'])

if __name__ == '__main__':
    try:
        config = load_config()
        model = create_model(config['model_path'])
        inference_loop(model, config)
    except Exception as e:
        print(f"Model error: {e}")
        exit(1) # Exit if model error
