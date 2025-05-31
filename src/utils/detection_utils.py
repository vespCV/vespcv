"""
Utility functions for image capture and detection.
"""

import os
import subprocess
from src.core.logger import logger
from src.core.config_loader import load_config

def capture_image():
    """Capture an image using libcamera-still and save it to the configured path.
    
    Returns:
        str: Path to the captured image
        
    Raises:
        FileNotFoundError: If the images folder doesn't exist
        subprocess.SubprocessError: If the camera capture fails
    """
    try:
        # Load configuration
        config = load_config()
        images_folder = config.get('images_folder')
        
        # Ensure images folder exists
        os.makedirs(images_folder, exist_ok=True)
        
        # Set up image path
        image_path = os.path.join(images_folder, 'image_for_detection.jpg')
        logger.debug(f"Capturing image to: {image_path}")
        
        # Capture image using libcamera-still
        subprocess.run([
            "libcamera-still",
            "-o", image_path,
            "--width", "4656",
            "--height", "3496"
        ], check=True)
        
        logger.debug(f"Image captured successfully: {image_path}")
        return image_path
        
    except FileNotFoundError as e:
        logger.error(f"Images folder not found: {e}")
        raise
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to capture image: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during image capture: {e}")
        raise

if __name__ == "__main__":
    # Test image capture
    try:
        image_path = capture_image()
        print(f"Test capture successful: {image_path}")
    except Exception as e:
        print(f"Test capture failed: {e}")