# Enhanced Image Saving System

## Overview
The VespaCV detector now saves ALL images where any class is detected, not just Vespa velutina (vvel). This ensures you have a complete record of all detections for analysis and training.

## What Gets Saved

### 1. **Main Detection Images** (`/home/vcv/vespcv/data/images/`)
- **Filename format**: `{class}-{confidence}-{timestamp}.jpg`
- **Examples**: 
  - `vvel-0.85-20250807-133810.jpg`
  - `amel-0.72-20250807-133810.jpg`
  - `vespsp-0.83-20250717-151436.jpg`
- **Purpose**: Easy access to all detected images with clear naming

### 2. **YOLO Training Data** (`/home/vcv/vespcv/data/yolo_jpg_txt/`)
- **Images**: Same filename format as main images
- **Annotations**: Corresponding `.txt` files with YOLO format bounding boxes
- **Purpose**: Training data for improving the model

### 3. **Annotated Images** (`/home/vcv/vespcv/data/images/image_after_inference.jpg`)
- **Filename**: Always `image_after_inference.jpg` (overwritten each time)
- **Purpose**: Shows bounding boxes and labels for GUI display

### 4. **Detection Log** (`/home/vcv/vespcv/data/logs/detections.log`)
- **Format**: CSV with columns: Timestamp, Primary_Class, Primary_Confidence, All_Detections, Image_Path
- **Purpose**: Complete record of all detections for analysis

## Supported Classes
The system detects and saves images for all these classes:
- **vvel**: Vespa velutina (Asian hornet) - Priority class
- **amel**: Apis mellifera (honey bee)
- **vcra**: Vespa crabro (European hornet)
- **vespsp**: Other Vespa species
- **vzon**: Vespa zonata

## File Organization

```
/home/vcv/vespcv/
├── data/
│   ├── images/                    # Main detection images
│   │   ├── vvel-0.85-20250807-133810.jpg
│   │   ├── amel-0.72-20250807-133810.jpg
│   │   └── image_after_inference.jpg
│   ├── yolo_jpg_txt/             # Training data
│   │   ├── vvel-0.85-20250807-133810.jpg
│   │   ├── vvel-0.85-20250807-133810.txt
│   │   └── ...
│   └── logs/
│       └── detections.log        # Detection history
```

## Detection Logic

### Primary Class Selection
1. **vvel** (class_id 3) is always prioritized if detected
2. Otherwise, the class with highest confidence is selected
3. All detected classes are logged in the detection data

### Confidence Threshold
- **Detection threshold**: 0.80 (from config)
- **Visual threshold**: 0.60 (for drawing bounding boxes)
- **Saving threshold**: Any detection above 0.80 is saved

## Usage Examples

### List All Detection Images
```bash
python3 list_detections.py
```

### Test Image Saving
```bash
python3 test_image_saving.py
```

### Test Camera
```bash
python3 test_camera.py
```

## Configuration

Key settings in `config/config.yaml`:
```yaml
# Detection threshold (0.0 - 1.0)
conf_threshold: 0.80

# Target species for detection
class_names: ['amel', 'vcra', 'vespsp', 'vvel', 'vzon']

# Camera settings
camera:
  lens_position: 10  # 10cm focus for bait
  gain: 1.0          # Reduced for stability
  timeout: 10000     # 10 second timeout
```

## Benefits

1. **Complete Record**: All detections are saved, not just vvel
2. **Training Data**: Automatic generation of YOLO training data
3. **Easy Access**: Clear filename format for quick identification
4. **Analysis Ready**: Comprehensive logging for data analysis
5. **Stable Operation**: Improved error handling and recovery

## Troubleshooting

### No Images Being Saved
1. Check camera functionality: `python3 test_camera.py`
2. Verify confidence threshold in config
3. Check disk space: `df -h`
4. Review logs: `tail -f data/logs/detector.log`

### Camera Issues
1. Test camera reset: The system automatically resets camera on failures
2. Check lens position: Should be 10 for 10cm bait distance
3. Verify gain settings: Reduced to 1.0 for stability

### File Organization
- Use `list_detections.py` to see all saved images
- Check `data/logs/detections.log` for detection history
- YOLO training data is in `data/yolo_jpg_txt/` 