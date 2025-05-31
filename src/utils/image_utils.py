from ultralytics import YOLO
import time
import os
import cv2

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
                cv2.putText(annotated_image, label, (x1, int(text_y)), cv2.FONT_HERSHEY_SIMPLEX, 5.0, (255, 255, 255), 2)

                output_path = os.path.join(config.get('images_folder'), 'annotated_image.jpg')
                cv2.imwrite(output_path, annotated_image)
                print(f"Annotated image saved to {output_path}")

    except Exception as e:
            print(f"Error: {e}")