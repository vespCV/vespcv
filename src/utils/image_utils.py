from ultralytics import YOLO
import time
import os
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
from threading import Lock
import logging
from typing import Optional, Tuple

class ImageHandler:
    def __init__(self, logger):
        self.logger = logger
        self._image_cache = {}
        self._lock = Lock()
        # Original camera resolution
        self.original_width = 4656
        self.original_height = 3496
        self.aspect_ratio = self.original_width / self.original_height  # Should be ~1.33 (4:3)
    
    def load_and_resize_image(self, image_path: str, target_size: tuple) -> Optional[Image.Image]:
        """Load and resize an image while maintaining aspect ratio.
        
        Args:
            image_path: Path to the image file
            target_size: (width, height) tuple for the target size
            
        Returns:
            PIL.Image.Image or None if loading fails
        """
        try:
            abs_path = os.path.abspath(image_path)
            if not os.path.exists(abs_path):
                self.logger.error(f"Image file not found: {abs_path}")
                return None
                
            with self._lock:
                # Load image using PIL
                img = Image.open(abs_path)
                
                # Calculate new dimensions maintaining aspect ratio
                target_width, target_height = target_size
                img_width, img_height = img.size
                
                # Calculate scaling factor based on the limiting dimension
                width_ratio = target_width / img_width
                height_ratio = target_height / img_height
                scale_factor = min(width_ratio, height_ratio)
                
                # Calculate new dimensions
                new_width = int(img_width * scale_factor)
                new_height = int(img_height * scale_factor)
                
                # Resize image using LANCZOS resampling for better quality
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return img
        except Exception as e:
            self.logger.error(f"Error loading image: {e}")
            return None
    
    def save_inference_image(self, image: np.ndarray, base_dir: str) -> Optional[str]:
        """Save the inference image and return its path."""
        try:
            images_dir = os.path.join(base_dir, 'data', 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(images_dir, f'image_after_inference_{timestamp}.jpg')
            
            cv2.imwrite(image_path, image)
            self.logger.info(f"Saved inference image to: {image_path}")
            return image_path
        except Exception as e:
            self.logger.error(f"Error saving inference image: {e}")
            return None

def create_placeholder_image(width: int, height: int, text: str = "No detection") -> Image.Image:
    """Create a placeholder image with text.
    
    Args:
        width: Width of the image
        height: Height of the image
        text: Text to display on the placeholder
        
    Returns:
        PIL.Image.Image
    """
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        ((width - text_width) // 2, (height - text_height) // 2),
        text, fill=(100, 100, 100), font=font
    )
    return img

def create_thumbnail(image_path: str, size: Tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
    """Create a thumbnail from an image file.
    
    Args:
        image_path: Path to the image file
        size: (width, height) tuple for the thumbnail size
        
    Returns:
        ImageTk.PhotoImage or None if loading fails
    """
    try:
        img = Image.open(image_path)
        img.thumbnail(size)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        logging.error(f"Failed to create thumbnail for {image_path}: {e}")
        return None

def save_annotated_image(image_path, raw_results, config):
    """Save an annotated image with bounding boxes and labels."""
    try:
        if raw_results:
            results = raw_results[0]
            annotated_image = results.orig_img.copy()
            class_names = results.names

        if results.boxes:
            for box in results.boxes:
                # Get coordinates as a list of floats
                coords = box.xyxy[0].tolist()
                # Convert coordinates to integers
                x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])

                class_id = int(box.cls[0])
                class_name = class_names[class_id]

                # Use integer coordinates for cv2.rectangle
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
                label = f'{class_name} {box.conf[0]:.2f}'
                
                # Use integer coordinate for the text position
                text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10
                cv2.putText(annotated_image, label, (x1, int(text_y)), cv2.FONT_HERSHEY_SIMPLEX, 15.0, (255, 255, 255), 15)

                output_path = os.path.join(config.get('images_folder'), 'annotated_image.jpg')
                cv2.imwrite(output_path, annotated_image)
                print(f"Annotated image saved to {output_path}")

    except Exception as e:
            print(f"Error: {e}")