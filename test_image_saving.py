#!/usr/bin/env python3
"""
Test script to verify enhanced image saving functionality.
"""

import os
import sys
import cv2
import numpy as np
from datetime import datetime

def create_test_image():
    """Create a test image for testing."""
    # Create a simple test image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (100, 100, 100)  # Gray background
    
    # Add some text
    cv2.putText(img, "Test Detection", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    
    return img

def test_image_saving():
    """Test the image saving functions."""
    print("Testing enhanced image saving functionality...")
    
    try:
        # Import the functions
        from src.core.config_loader import load_config
        from src.utils.detection_utils import save_main_detection_image, save_archived_image
        
        # Load config
        config = load_config()
        print("✓ Configuration loaded")
        
        # Create test image
        test_img = create_test_image()
        print("✓ Test image created")
        
        # Create test detection data
        test_detections = {
            "class": "vvel",
            "confidence": "0.85",
            "timestamp": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "should_archive": True,
            "all_detections": [
                {"class": "vvel", "confidence": 0.85, "class_id": 3},
                {"class": "amel", "confidence": 0.72, "class_id": 0}
            ]
        }
        
        # Test saving main detection image
        main_path = save_main_detection_image(test_img, test_detections, config)
        if main_path and os.path.exists(main_path):
            print(f"✓ Main detection image saved: {main_path}")
        else:
            print("✗ Failed to save main detection image")
            return False
        
        # Test saving archived image
        archive_path = save_archived_image(test_img, test_detections, config)
        if archive_path and os.path.exists(archive_path):
            print(f"✓ Archived image saved: {archive_path}")
        else:
            print("✗ Failed to save archived image")
            return False
        
        # Test with different class
        test_detections2 = {
            "class": "amel",
            "confidence": "0.72",
            "timestamp": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "should_archive": True,
            "all_detections": [
                {"class": "amel", "confidence": 0.72, "class_id": 0}
            ]
        }
        
        main_path2 = save_main_detection_image(test_img, test_detections2, config)
        if main_path2 and os.path.exists(main_path2):
            print(f"✓ Second detection image saved: {main_path2}")
        else:
            print("✗ Failed to save second detection image")
            return False
        
        print("\n✓ All image saving tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Enhanced Image Saving Test")
    print("=" * 50)
    
    success = test_image_saving()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! Enhanced image saving is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 