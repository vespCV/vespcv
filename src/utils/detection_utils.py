"""
Utility functions for image capture and detection.
"""

import os
import subprocess
import cv2
from src.core.logger import logger
from src.core.config_loader import load_config
import time
import json

def log_detection_data(detections, image_path):
    """Log detection data to a detections.log file in CSV format.
    
    Args:
        detections: Dictionary containing detection information
        image_path: Path to the detected image
    """
    try:
        # Skip logging if no detection was made
        if detections.get('class') == 'no_detection':
            return
            
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join('data', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Prepare log entry
        timestamp = detections.get('timestamp', time.strftime("%Y%m%d-%H%M%S"))
        class_name = detections.get('class', 'no_detection')
        confidence = detections.get('confidence', '0.00')
        
        # Write to log file
        log_path = os.path.join(logs_dir, 'detections.log')
        
        # Check if file exists to write header
        file_exists = os.path.exists(log_path)
        
        with open(log_path, 'a') as f:
            # Write header if file is new
            if not file_exists:
                f.write("Timestamp,Class,Confidence,Image Path\n")
            
            # Write data row
            f.write(f"{timestamp},{class_name},{confidence},{image_path}\n")
            
        logger.debug(f"Detection data logged to {log_path}")
        
    except Exception as e:
        logger.error(f"Error logging detection data: {e}")

def reset_camera():
    """Reset the Arducam IMX519 camera by unloading and reloading the driver."""
    try:
        # First try to stop any running camera processes
        subprocess.run(['sudo', 'pkill', '-f', 'libcamera'], check=False)
        time.sleep(1)  # Wait for processes to stop
        
        # Unload the camera driver
        subprocess.run(['sudo', 'modprobe', '-r', 'arducam_imx519'], check=False)
        time.sleep(2)  # Increased wait time for driver to unload
        
        # Reload the camera driver
        subprocess.run(['sudo', 'modprobe', 'arducam_imx519'], check=False)
        time.sleep(3)  # Increased wait time for driver to initialize
        
        # Verify camera is available
        try:
            # Quick test capture to verify camera is working
            test_path = "/tmp/test_capture.jpg"
            subprocess.run([
                "libcamera-still",
                "--nopreview",
                "-o", test_path,
                "--width", "1920",
                "--height", "1440",
                "--timeout", "2000"
            ], check=True, timeout=5)
            
            # Clean up test image
            if os.path.exists(test_path):
                os.remove(test_path)
                
            logger.info("Camera reset completed and verified")
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Camera verification failed after reset: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to reset camera: {e}")
        return False

def capture_image(max_retries=3):
    """Capture an image using libcamera-still and save it to the configured path.
    Uses retry/reset logic only for Arducam.
    Args:
        max_retries (int): Maximum number of retry attempts if capture fails (Arducam only)
    Returns:
        str: Path to the captured image
    Raises:
        FileNotFoundError: If the images folder doesn't exist
        subprocess.SubprocessError: If the camera capture fails after all retries
    """
    try:
        # Load configuration
        config = load_config()
        images_folder = config.get('images_folder')
        camera_type = config.get('camera_type', 'pi')
        autofocus_enabled = config['camera'].get('autofocus_enabled', True)  # Get autofocus setting
        autofocus_mode = config['camera'].get('autofocus_mode', False)  # Get autofocus mode setting
        lens_position = config['camera'].get('lens_position', 10)  # Get lens position
        gain = config['camera'].get('gain', 1.0)  # Get gain value
        
        # Ensure images folder exists
        os.makedirs(images_folder, exist_ok=True)
        
        # Set up image path
        image_path = os.path.join(images_folder, 'image_for_detection.jpg')
        logger.debug(f"Capturing image to: {image_path}")
        
        # Use a more stable resolution (1920x1440)
        width = "1920"
        height = "1440"
        
        if camera_type == 'arducam':
            retry_count = 0
            while retry_count < max_retries:
                try:
                    # Prepare command options
                    command = [
                        "libcamera-still",
                        "--nopreview",
                        "-o", image_path,
                        "--width", width,
                        "--height", height,
                        "--ev", "0.5",  # Adjust exposure compensation
                        "--gain", str(gain),  # Include gain in the command
                        "--timeout", "5000"
                    ]
                    
                    # Add autofocus options if enabled
                    if autofocus_mode:  # Use autofocus if true
                        command.extend([
                            "--autofocus-mode", "continuous"
                        ])
                    else:  # Use fixed lens position
                        command.extend([
                            "--lens", str(lens_position)  # Focus on specified lens position
                        ])
                    
                    subprocess.run(command, check=True, timeout=10)  # Add command timeout
                    
                    # Verify the image was created and is valid
                    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                        logger.debug(f"Image captured successfully: {image_path}")
                        return image_path
                    else:
                        raise subprocess.SubprocessError("Image file not created or empty")
                        
                except subprocess.SubprocessError as e:
                    retry_count += 1
                    logger.warning(f"Capture attempt {retry_count} failed: {e}")
                    if retry_count < max_retries:
                        logger.info("Attempting to reset camera...")
                        if reset_camera():
                            time.sleep(3)  # Increased wait time after reset
                            continue
                        else:
                            logger.error("Failed to reset camera")
                            break
                    else:
                        logger.error(f"Failed to capture image after {max_retries} attempts")
                        raise
        else:  # camera_type == 'pi' or unknown
            # Standard single-attempt logic for Pi Camera Module 3
            subprocess.run([
                "libcamera-still",
                "--nopreview",
                "-o", image_path,
                "--width", width,
                "--height", height,
                "--gain", str(gain),  # Include gain in the command
                "--timeout", "5000",
                "--autofocus-mode", "continuous",
                "--framerate", "30"
            ], check=True, timeout=10)
            
            # Verify the image was created and is valid
            if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                logger.debug(f"Image captured successfully: {image_path}")
                return image_path
            else:
                raise subprocess.SubprocessError("Image file not created or empty")
        
    except FileNotFoundError as e:
        logger.error(f"Images folder not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during image capture: {e}")
        raise

def save_annotated_image(image, results, config):
    """Save the annotated image.
    
    Args:
        image: The image to annotate
        results: The detection results
        config: Configuration dictionary
        
    Returns:
        str: Path to the saved annotated image
    """
    try:
        if results:
            # Create and save the annotated version
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
                    cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 10)
                    label = f'{class_name} {box.conf[0]:.2f}'
                    
                    # Draw label
                    text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10
                    cv2.putText(annotated_image, label, (x1, int(text_y)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 15.0, (0, 255, 0), 15)

            # Save the annotated image with the consistent name
            output_path = os.path.join(config.get('images_folder'), 'image_after_inference.jpg')
            cv2.imwrite(output_path, annotated_image)
            logger.debug(f"Annotated image saved to {output_path}")

            return output_path

    except Exception as e:
        logger.error(f"Error saving images: {e}")
        return None

def save_original_image(config, detections=None, results=None):
    """Save the original image with detection metadata in the filename and create a YOLO format text file.
    
    Args:
        config: Configuration dictionary
        detections: Dictionary containing detection information (optional)
        results: YOLO detection results containing bounding boxes (optional)
        
    Returns:
        str: Path to the saved original image
    """
    try:
        # Create the new yolo_jpg_txt directory
        yolo_dir = os.path.join('data', 'yolo_jpg_txt')
        os.makedirs(yolo_dir, exist_ok=True)
        
        # Load configuration
        images_folder = config.get('images_folder')
        original_image_path = os.path.join(images_folder, 'image_for_detection.jpg')
        
        # Check if the original image exists
        if not os.path.exists(original_image_path):
            logger.error(f"Original image not found: {original_image_path}")
            return None
        
        # If we have detection metadata, use it for the filename
        if detections and detections.get("should_archive"):
            class_name = detections["class"]
            confidence = detections["confidence"]
            timestamp = detections["timestamp"]
            base_filename = f"{class_name}-{confidence}-{timestamp}"
        else:
            # Fallback to the old behavior if no detection metadata
            base_filename = f"_{os.path.basename(original_image_path)}"
            
        # Save the image
        new_image_path = os.path.join(yolo_dir, f"{base_filename}.jpg")
        cv2.imwrite(new_image_path, cv2.imread(original_image_path))
        logger.debug(f"Original image saved to {new_image_path}")
        
        # Log detection data
        if detections:
            log_detection_data(detections, new_image_path)
        
        # If we have YOLO results, create the YOLO format text file
        if results and results.boxes:
            # Get the image dimensions for normalization
            img = cv2.imread(original_image_path)
            img_height, img_width = img.shape[:2]
            
            # Create the text file with the same base name
            txt_path = os.path.join(yolo_dir, f"{base_filename}.txt")
            
            with open(txt_path, 'w') as f:
                for box in results.boxes:
                    # Get normalized coordinates (x_center, y_center, width, height)
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    class_id = int(box.cls[0])
                    
                    # Convert to YOLO format (normalized)
                    x_center = (x1 + x2) / (2 * img_width)
                    y_center = (y1 + y2) / (2 * img_height)
                    width = (x2 - x1) / img_width
                    height = (y2 - y1) / img_height
                    
                    # Write in YOLO format: class_id x_center y_center width height
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            logger.debug(f"YOLO format text file saved to {txt_path}")
        
        return new_image_path

    except Exception as e:
        logger.error(f"Error saving original image: {e}")
        return None

def save_archived_image(image, detections, config):
    """Save an archived image with detection information in the filename.
    
    Args:
        image: The image to save
        detections: Dictionary containing detection information
        config: Configuration dictionary
        
    Returns:
        str: Path to the saved archived image
    """
    try:
        if detections.get("should_archive"):
            class_name = detections["class"]
            confidence = detections["confidence"]
            timestamp = detections["timestamp"]
            archive_filename = f"{class_name}-{confidence}-{timestamp}.jpg"
            archive_path = os.path.join(config['images_folder'], archive_filename)
            cv2.imwrite(archive_path, image)
            logger.debug(f"Archived detection image: {archive_path}")
            return archive_path
        return None
    except Exception as e:
        logger.error(f"Error saving archived image: {e}")
        return None

def initialize_application():
    """Initialize all core components of the application."""
    try:
        # Load configuration
        config = load_config()
        
        # Create necessary directories first, before any logging
        required_dirs = [
            os.path.dirname(config['log_file_path']),  # Create logs directory
            config['images_folder'],                   # Create images directory
            'data/yolo_jpg_txt'                       # Create yolo directory
        ]
        
        for dir_path in required_dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")  # Use print instead of logger since logger isn't configured yet
        
        # Now that directories exist, configure logging
        configure_logger(config['log_file_path'])
        start_temperature_logging()
        
        logger.info("Application initialized successfully")
        return config
    except Exception as e:
        print(f"Failed to initialize application: {e}")  # Use print instead of logger
        raise

if __name__ == "__main__":
    # Test image capture
    try:
        image_path = capture_image()
        print(f"Test capture successful: {image_path}")
    except Exception as e:
        print(f"Test capture failed: {e}")