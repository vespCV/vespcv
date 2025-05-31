"""
Utility functions for image capture and detection.
"""

import os
import subprocess
import cv2
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

def save_annotated_image(image, results, config):
    """Save an annotated image with bounding boxes and labels.
    
    Args:
        image: The image to annotate
        results: The detection results
        config: Configuration dictionary
        
    Returns:
        str: Path to the saved annotated image
    """
    try:
        if results:
            annotated_image = image.copy()
            class_names = results.names

            if results.boxes:
                for box in results.boxes:
                    # Get coordinates as a list of floats
                    coords = box.xyxy[0].tolist()
                    # Convert coordinates to integers
                    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])

                    class_id = int(box.cls[0])
                    class_name = class_names[class_id]

                    # Draw bounding box
                    cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
                    label = f'{class_name} {box.conf[0]:.2f}'
                    
                    # Draw label
                    text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10
                    cv2.putText(annotated_image, label, (x1, int(text_y)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 15.0, (255, 255, 255), 15)

            # Save the annotated image
            output_path = os.path.join(config.get('images_folder'), 'annotated_image.jpg')
            cv2.imwrite(output_path, annotated_image)
            logger.debug(f"Annotated image saved to {output_path}")
            return output_path

    except Exception as e:
        logger.error(f"Error saving annotated image: {e}")
        return None

if __name__ == "__main__":
    # Test image capture
    try:
        image_path = capture_image()
        print(f"Test capture successful: {image_path}")
    except Exception as e:
        print(f"Test capture failed: {e}")