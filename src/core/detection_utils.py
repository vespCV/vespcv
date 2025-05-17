import yaml
import os
import subprocess

from config_loader import load_config


def capture_image():
    """Capture an image using libcamera-still and save it to the configured path.
    
    Returns:
        str: Path to the captured image
    """
    try:
        config = load_config()  # Loads the config dict
        images_folder = config.get('images_folder', '/default/path')  # Safely get the value, with a fallback
        image_path = os.path.join(images_folder, 'image_for_detection.jpg')
        print(f"Attempting to save image to: {image_path}")  # Debug print
        subprocess.run([ 
            "libcamera-still",
            "-o", image_path,  # Save the image_for_detection.jpg
            "--width", "4656",
            "--height", "3496"
        ])
        return image_path
    except KeyError as e:
        print(f"Error: Missing key in config: {e}")
        raise e  # Or handle it appropriately
    except Exception as e:
        print(f"Error: {e}")
        raise e


if __name__ == "__main__":
    print("Starting image capture...")  # Debug print
    result = capture_image()
    print(f"Image captured at: {result}")  # Debug print