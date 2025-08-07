#!/usr/bin/env python3
"""
Simple camera test script to verify camera functionality.
Run this before starting the main detector to ensure camera is working.
"""

import os
import sys
import subprocess
import time

def test_camera():
    """Test camera functionality with basic capture."""
    print("Testing camera functionality...")
    
    # Test image path
    test_path = "/tmp/camera_test.jpg"
    
    try:
        # Simple camera test command
        command = [
            "libcamera-still",
            "--nopreview",
            "-o", test_path,
            "--width", "640",
            "--height", "480",
            "--timeout", "5000",
            "--immediate"
        ]
        
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if os.path.exists(test_path) and os.path.getsize(test_path) > 1000:
                print("✓ Camera test successful!")
                print(f"  Image saved: {test_path}")
                print(f"  Image size: {os.path.getsize(test_path)} bytes")
                
                # Clean up test image
                os.remove(test_path)
                return True
            else:
                print("✗ Camera test failed: Image file not created or too small")
                return False
        else:
            print(f"✗ Camera test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Camera test failed: Timeout")
        return False
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from src.core.config_loader import load_config
        config = load_config()
        print("✓ Configuration loaded successfully")
        print(f"  Camera type: {config.get('camera_type', 'unknown')}")
        print(f"  Capture interval: {config.get('capture_interval', 'unknown')} seconds")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("VespaCV Camera Test")
    print("=" * 50)
    
    # Test configuration first
    config_ok = test_config()
    
    # Test camera
    camera_ok = test_camera()
    
    print("\n" + "=" * 50)
    if config_ok and camera_ok:
        print("✓ All tests passed! Camera should work with the detector.")
        return 0
    else:
        print("✗ Some tests failed. Please check camera setup and configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 