from ultralytics import YOLO
import yaml
import time
import os

from detection_utils import capture_image

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
        print("Error: Failed to load YOLO model.")
        raise e
    return model


if __name__ == '__main__':
    try:
        config = load_config()
    except Exception as e:
        print(f"Config error: {e}")
        exit(1) # Exit if config error

    try:
        model = create_model(config['model_path'])
    except Exception as e:
        print(f"Model error: {e}")
        exit(1) # Exit if model error

    while True:
        """
        Capture an image, run inference
        """
        try:
            image_path = capture_image() # Capture the image
            # Update the image path (in case in the future we want to save more images, so it gets the latest image)
            image_folder = config.get('images_folder')
            image_path = os.path.join(image_folder, 'image_for_detection.jpg')
            results = model(image_path) # Run inference
            print(results) #TEST HIER VERDER MET VERWERKEN VAN RESULTS
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(config['capture_interval'])
