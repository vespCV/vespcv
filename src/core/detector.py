"""
This file is the main file for the detector.
It loads the configuration, creates the model, and runs the inference.
"""


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
        print(f"Error {e}: Failed to load YOLO model.")
        raise e
    return model

def run_inference(config, model):
    """Capture an image, run inference, returns raw results"""
    # Update the image path (in case in the future we want to save more images, so it gets the latest image)
    image_folder = config.get('images_folder')

    # Capture the image
    image_path = capture_image()

    # Setting image path to the latest image in the images folder
    image_path = os.path.join(image_folder, 'image_for_detection.jpg')
    # TODO after gui is ready: make this dynamic and not hardcoded   
    
    # Run YOLO inference on the image
    results = model(image_path)
    # TODO: process results
    print(results)
    return raw_results

    
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
        # Main loop for continuous inference cycles
        try:
            #Run one cycle op image capture and inference
            raw_results = run_inference(config, model)

            print(raw_results)

        except Exception as e:
        # TODO: add logging and catch specific errors
            print(f"Error: {e}") 
       
    # Controls the capture interval as specified in config file
    time.sleep(config['capture_interval'])
