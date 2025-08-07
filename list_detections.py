#!/usr/bin/env python3
"""
Script to list all saved detection images and show the file structure.
"""

import os
import glob
from datetime import datetime

def list_detection_images():
    """List all detection images in the system."""
    print("Detection Images Overview")
    print("=" * 50)
    
    # Check main images folder
    main_images_dir = "/home/vcv/vespcv/data/images"
    if os.path.exists(main_images_dir):
        print(f"\nMain Images Folder: {main_images_dir}")
        print("-" * 30)
        
        # Find all detection images (files with class names)
        detection_files = []
        for class_name in ['vvel', 'amel', 'vcra', 'vespsp', 'vzon']:
            pattern = os.path.join(main_images_dir, f"{class_name}-*.jpg")
            files = glob.glob(pattern)
            detection_files.extend(files)
        
        if detection_files:
            # Sort by modification time (newest first)
            detection_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            print(f"Found {len(detection_files)} detection images:")
            for i, file_path in enumerate(detection_files[:10], 1):  # Show last 10
                filename = os.path.basename(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                size = os.path.getsize(file_path)
                print(f"  {i:2d}. {filename}")
                print(f"      Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      Size: {size:,} bytes")
            
            if len(detection_files) > 10:
                print(f"  ... and {len(detection_files) - 10} more files")
        else:
            print("No detection images found")
    
    # Check YOLO directory
    yolo_dir = "/home/vcv/vespcv/data/yolo_jpg_txt"
    if os.path.exists(yolo_dir):
        print(f"\nYOLO Training Data Folder: {yolo_dir}")
        print("-" * 30)
        
        jpg_files = glob.glob(os.path.join(yolo_dir, "*.jpg"))
        txt_files = glob.glob(os.path.join(yolo_dir, "*.txt"))
        
        if jpg_files:
            print(f"Found {len(jpg_files)} image files and {len(txt_files)} annotation files")
            
            # Show some examples
            for i, file_path in enumerate(jpg_files[:5], 1):
                filename = os.path.basename(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  {i}. {filename} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            
            if len(jpg_files) > 5:
                print(f"  ... and {len(jpg_files) - 5} more files")
        else:
            print("No YOLO training files found")
    
    # Check logs
    logs_dir = "/home/vcv/vespcv/data/logs"
    if os.path.exists(logs_dir):
        detections_log = os.path.join(logs_dir, "detections.log")
        if os.path.exists(detections_log):
            print(f"\nDetection Log: {detections_log}")
            print("-" * 30)
            
            with open(detections_log, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:  # Has header and data
                    print(f"Total log entries: {len(lines) - 1}")
                    
                    # Show last 5 entries
                    print("Last 5 detections:")
                    for line in lines[-5:]:
                        if line.strip() and not line.startswith("Timestamp"):
                            parts = line.strip().split(',')
                            if len(parts) >= 3:
                                timestamp = parts[0]
                                class_name = parts[1]
                                confidence = parts[2]
                                print(f"  {timestamp} - {class_name} ({confidence})")
                else:
                    print("Log file is empty or only contains header")

def main():
    """Main function."""
    try:
        list_detection_images()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 