"""
This file is the main file for the detector.
It loads the configuration, creates the model, and runs the inference.
"""

from ultralytics import YOLO
import yaml
import time
import os
import cv2 # OpenCV

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

def perform_inference(model, image_path):
    """Run inference, returns raw results"""
    # Run YOLO inference on the image
    results = model(image_path)
    return results  # Return the raw results

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
            # Capture the image
            image_path = capture_image()

            # Run one cycle of image capture and inference
            raw_results = perform_inference(model, image_path)

            if raw_results:  # Check if results are not empty
                results = raw_results[0]  # Get the first result
                annotated_image = results.orig_img.copy()  # Get the image and make a copy for bounding box drawing
                class_names = results.names  # Get the class name mapping

                # Check if any boxes were detected before trying to loop
                if results.boxes:
                    # Iterate through each detected box
                    for box in results.boxes:
                        # Get coordinates of the bounding box
                        x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0]]  # Get int coordinates

                        # Get confidence
                        confidence = box.conf[0]

                        # Get class name ID and name
                        class_id = int(box.cls[0])
                        class_name = class_names[class_id]

                        # Draw bounding box (Red color, thickness 4)
                        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 0, 255), 4)

                        # Prepare label text
                        label = f'{class_name} {confidence:.2f}'

                        # Determine text position
                        # Put text at the top left corner of the bounding box if space,
                        # otherwise inside the bounding box
                        text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10

                        # Put text on the image (white color, font scale 0.5, thickness 1)
                        cv2.putText(annotated_image, label, (x1, text_y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Save or display the annotated image
                output_path = os.path.join(config.get('images_folder'), 'annotated_image.jpg')
                cv2.imwrite(output_path, annotated_image)  # Save the annotated image
                print(f"Annotated image saved to {output_path}")

        except Exception as e:
            # TODO: add logging and catch specific errors
            print(f"Error: {e}")

        # Controls the capture interval as specified in config file
        time.sleep(config['capture_interval'])
