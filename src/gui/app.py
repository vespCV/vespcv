import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import scrolledtext # Import scrolledtext for a text area with a scrollbar
import threading
import time
import os
from PIL import Image, ImageTk  # Import PIL for image handling
import cv2
import queue
import logging
from threading import Lock
from typing import Optional, List, Dict
import numpy as np
from src.core.detector import DetectionController

class ImageHandler:
    def __init__(self, logger):
        self.logger = logger
        self._image_cache = {}
        self._lock = Lock()
    
    def load_and_resize_image(self, image_path: str, target_size: tuple) -> Optional[Image.Image]:
        """Load and resize an image while maintaining aspect ratio."""
        try:
            abs_path = os.path.abspath(image_path)
            if not os.path.exists(abs_path):
                self.logger.error(f"Image file not found: {abs_path}")
                return None
                
            with self._lock:
                img = Image.open(abs_path)
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
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

class vespcvGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aziatisch-/Geelpotige Hoornaar Detector")
        self.geometry("1024x768")
        self.configure(bg="#FFF8E1") # Light amber background

        # Initialize detection state
        self.is_detecting = False
        self.detection_thread = None

        # Configure styles for custom buttons
        style = ttk.Style()
        style.configure('Red.TButton', background='red', foreground='black') # Config style for power off button
        style.configure('Orange.TButton', background='orange', foreground='black') # Config style for stop detection button
        style.configure('Green.TButton', background='green', foreground='black') # Config style for start detection buttong

        # Call methods to create different parts of the GUI
        self.create_header()
        self.create_main_content()
        self.create_control_frame()
        # We will add log frame later

        # Initialize image queue
        self.image_queue = queue.Queue()

        # Initialize logger
        self.logger = logging.getLogger(__name__)

        self._cleanup_handlers = []

        self.image_lock = Lock()

        # Initialize image handler
        self.image_handler = ImageHandler(self.logger)

        # Initialize DetectionController
        self.detector = DetectionController(self.handle_detection_result)
        self.detector.start()  # Start detection on launch

        self.show_captured_image()

    def create_header(self):
        # This method will create the header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Add the main title
        ttk.Label(header_frame, text="Aziatisch-/Geelpotige Hoornaar Detector", font=("Arial", 24, "bold")).pack(side=tk.LEFT, expand=True)
        ttk.Button(header_frame, text="UITZETTEN", style='Red.TButton').pack(side=tk.RIGHT, padx=2)
        ttk.Button(header_frame, text="STOP DETECTIE", style='Orange.TButton').pack(side=tk.RIGHT, padx=2) 
        ttk.Button(header_frame, text="START DETECTIE", style='Green.TButton').pack(side=tk.RIGHT, padx=2) 

    def create_main_content(self):
        # Main area with live feed, detections, and charts
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Left and right frames within the main frame
        # Right frame first to see if it influences space allocation
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5) 

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5) 

        # Methods to populate these frames
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent_frame):
        # This method will contain the Captured Image and Charts

        # Captured Image section (takes up the top part of the left panel)
        live_feed_frame = ttk.LabelFrame(parent_frame, text="Vastgelegde afbeelding") # Captured image
        live_feed_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Placeholder for the captured image display (using a Canvas)
        self.live_feed_canvas = tk.Canvas(live_feed_frame, bg="gray", width=400, height=300)  # Set a fixed size
        self.live_feed_canvas.pack(expand=True, fill=tk.BOTH)

        # Charts section (takes up the bottom part of the left panel)
        charts_frame = ttk.Frame(parent_frame) # Frame to hold the two charts side-by-side
        charts_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Add placeholder methods for the individual charts within the charts_frame
        self.create_insect_count_chart(charts_frame) # Bar chart
        self.create_detection_timeline_chart(charts_frame) # Line chart

    def create_insect_count_chart(self, parent_frame):
        # This method will create the Insect Detection Count bar chart
        bar_chart_frame = ttk.LabelFrame(parent_frame, text="Insecten detectie teller")
        bar_chart_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5) # Pack to the left in the charts_frame

        # Create a matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(4, 3)) # Adjust figsize as needed

        # Placeholder data (replace with real data later)
        insects = ['vvel', 'vcra', 'amel', 'vesp', 'zon']
        counts = [12, 8, 5, 15, 0]
        ax.bar(insects, counts, color='#FFA000') # Use a color that fits your scheme
        ax.set_ylabel('Count')

        # Embed the matplotlib figure in the Tkinter widget
        canvas = FigureCanvasTkAgg(fig, master=bar_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def create_detection_timeline_chart(self, parent_frame):
        # This method will create the Detection Timeline line chart
        line_chart_frame = ttk.LabelFrame(parent_frame, text="Detectie tijdlijn")
        line_chart_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5) # Pack to the left in the charts_frame, next to the bar chart

        # Create a matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(4, 3)) # Adjust figsize as needed (same as bar chart for consistency)

        # Placeholder data (replace with real data later)
        times = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00']
        detections = [2, 1, 0, 3, 5, 2]
        ax.plot(times, detections, color='#FFA000', marker='o') # Use a color that fits your scheme and add markers
        ax.set_ylabel('Detections')
        ax.set_title('Detection Timeline')
        ax.tick_params(axis='x', rotation=45) # Rotate x-axis labels if they overlap

        # Embed the matplotlib figure in the Tkinter widget
        canvas = FigureCanvasTkAgg(fig, master=line_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def create_right_panel(self, parent_frame):
        # This method will contain Saved Detections and Logs

        # Saved Detections section (takes up the top part of the right panel)
        saved_detections_frame = ttk.LabelFrame(parent_frame, text="Opgeslagen detecties") #Saved detections
        saved_detections_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5) # Saved Detections will take up the top part of the right frame

        # Add content to the Saved Detections frame
        self.create_saved_detections_section(saved_detections_frame)

        # System Logs section (takes up the bottom part of the right panel)
        log_frame = ttk.LabelFrame(parent_frame, text="System Logs")
        log_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5) # Logs will take up the bottom part

        # Add placeholder method for the log display within the log_frame
        self.create_log_display(log_frame)

    def create_saved_detections_section(self, parent_frame):
        """This method will create the content inside the Saved Detections LabelFrame"""
        
        # Frame for filter and download controls
        controls_frame = ttk.Frame(parent_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        # Filter button
        ttk.Button(controls_frame, text="Alleen Vespa velutina").pack(side=tk.LEFT, padx=5)  # Detect only Vespa velutina

        # Download button
        ttk.Button(controls_frame, text="Download").pack(side=tk.RIGHT, padx=5)

        # Frame for the detection grid placeholders
        detections_grid_frame = ttk.Frame(parent_frame)
        detections_grid_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Load images that start with "vvel"
        images_folder = '/home/vcv/vespcv/data/images'  # Update to your images folder path
        vvel_images = [f for f in os.listdir(images_folder) if f.startswith('vvel')]
        
        # Extract confidence scores and sort images
        image_data = []
        for image in vvel_images:
            parts = image.split('-')
            if len(parts) >= 4:  # Ensure the filename has the expected format
                confidence_score = float(parts[1])
                time_part = parts[3].split('.')[0]  # '215530.jpg' -> '215530'
                image_data.append((image, confidence_score, time_part))

        # Sort by confidence score in descending order and take the top 4
        image_data.sort(key=lambda x: x[1], reverse=True)
        top_images = image_data[:4]  # Get the top 4 images

        # Add image frames to the grid
        for i, (image_name, _, time_part) in enumerate(top_images):
            image_path = os.path.join(images_folder, image_name)
            img = Image.open(image_path)
            img.thumbnail((100, 100))  # Resize image to fit in the frame
            photo = ImageTk.PhotoImage(img)

            # Create a frame for each image
            placeholder_frame = ttk.Frame(detections_grid_frame, width=100, height=120)
            placeholder_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=6)

            # Add the image to the frame
            label = ttk.Label(placeholder_frame, image=photo)
            label.image = photo  # Keep a reference to avoid garbage collection
            label.pack(expand=True, fill=tk.BOTH)

            # Format timestamp to hh:mm:ss
            if len(time_part) == 6:
                formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
            else:
                formatted_time = time_part  # fallback

            ttk.Label(placeholder_frame, text=formatted_time, anchor="center").pack(expand=True, fill=tk.BOTH)

    def create_log_display(self, parent_frame):
        # Create the log display area
        # Using ScrolledText for a text area with a built-in scrollbar
        self.log_text = scrolledtext.ScrolledText(parent_frame, state='disabled', wrap='word') # Use state='disabled' to make it read-only
        self.log_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

    def create_control_frame(self):
        # This method will create the control buttons (Start/Stop Detection)
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    def start_detection(self):
        self.detector.start()

    def stop_detection(self):
        self.detector.stop()

    def inference_loop(self, model, config):
        while True:
            try:
                image = self._capture_and_process_image(model, config)
                self._save_detection_results(image, config)
                self._update_ui(image)
            except Exception as e:
                self.logger.error(f"Inference error: {e}")

    def _capture_and_process_image(self, model, config):
        image_path = capture_image()  # Ensure this function handles errors
        print(f"Captured image path: {image_path}")  # Debug print

        # Load the full image (no magnification)
        img = cv2.imread(image_path)

        # Apply YOLO inference to the full image
        results = model(img)[0]

        # Initialize variables to track detections
        detected_classes = {}  # Dictionary to count occurrences of each class
        class_3_detected = False  # Flag for class 3 detection

        # Check for class detection with high confidence
        for result in results.boxes.data.tolist():  # Each detection in format [x1, y1, x2, y2, conf, class]
            x1, y1, x2, y2, conf, cls = result[:6]
            if conf > config.get('conf_threshold', 0.8):  # Use threshold from config
                # Draw the bounding box
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  # Green box

                # Get the class name from the config
                class_name = config['class_names'][int(cls)]  # Assuming cls is an index
                detected_classes[int(cls)] = detected_classes.get(int(cls), 0) + 1  # Count occurrences

                # Optionally, add a label with class name and confidence
                label = f"Class: {class_name}, Conf: {conf:.2f}"
                cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Check if class 3 is detected
                if int(cls) == 3:
                    class_3_detected = True

        # Determine the class name for the filename
        if class_3_detected:
            final_class_name = "vvel"
        else:
            # Find the most detected species
            most_detected_class = max(detected_classes, key=detected_classes.get, default=None)
            if most_detected_class is not None:
                final_class_name = config['class_names'][most_detected_class]  # Use the name of the most detected class
            else:
                print("No classes detected; image not saved.")  # Debug print
                return None  # Skip saving the image if no classes are detected

        # Format the filename with the determined class name and confidence score
        confidence_score = f"{conf:.2f}"  # Use the last detected confidence score
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format time and date
        new_image_name = f"{final_class_name}-{confidence_score}-{timestamp}.jpg"  # Use final class name
        new_image_path = os.path.join('data/images', new_image_name)

        # Save the full image with the new filename
        cv2.imwrite(new_image_path, img)  # Save the full image
        print(f"Saved image: {new_image_path}")  # Debug print

        # Save the image after inference with bounding boxes
        after_inference_image_path = os.path.join('data/images/', 'image_after_inference.jpg')
        cv2.imwrite(after_inference_image_path, img)  # Save the image with bounding boxes
        print(f"Saved image after inference: {after_inference_image_path}")  # Debug print

        # Update the live feed with the new image
        print(f"Updating live feed with image: {after_inference_image_path}")  # Debug print
        self.update_live_feed(after_inference_image_path)

        self.show_captured_image()

        return after_inference_image_path

    def _save_detection_results(self, image_path, config):
        # Implementation of _save_detection_results method
        pass

    def _update_ui(self, image_path):
        self.update_live_feed(image_path)

    def update_live_feed(self, image_path: str) -> None:
        """Update the live feed canvas with the new image."""
        with self.image_lock:
            for attempt in range(3):
                try:
                    img = Image.open(image_path)
                    img.thumbnail((400, 300))
                    photo = ImageTk.PhotoImage(img)
                    self.live_feed_canvas.delete("all")
                    self.live_feed_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                    self.live_feed_canvas.image = photo
                    self.update()
                    break  # Success!
                except Exception as e:
                    self.logger.error(f"Failed to update live feed (attempt {attempt+1}): {e}")
                    time.sleep(0.2)  # Wait a bit and try again

    def show_captured_image(self):
        image_path = '/home/vcv/vespcv/data/images/image_after_inference.jpg'
        time.sleep(0.5)  # Add a 0.5 second delay to avoid file write/read race
        if os.path.exists(image_path):
            self.update_live_feed(image_path)
        else:
            self.live_feed_canvas.delete("all")

    def __del__(self):
        for handler in self._cleanup_handlers:
            handler()

    def handle_detection_result(self, result):
        # Use self.after() to update GUI elements safely
        self.after(0, self.update_gui_with_result, result)

    def update_gui_with_result(self, result):
        """
        Update the GUI with the latest detection result.
        :param result: dict with keys 'image_path' and 'detection' (class, confidence, timestamp)
        """
        # 1. Update live feed
        image_path = result.get("image_path")
        if image_path and os.path.exists(image_path):
            self.update_live_feed(image_path)

        # 2. Update logs
        detection = result.get("detection", {})
        log_entry = (
            f"{detection.get('timestamp', '')} - "
            f"Class: {detection.get('class', '')}, "
            f"Confidence: {detection.get('confidence', '')}\n"
        )
        self.log_text.config(state='normal')
        self.log_text.insert('end', log_entry)
        self.log_text.see('end')
        self.log_text.config(state='disabled')

        # 3. Update charts (example: increment detection count)
        detected_class = detection.get('class')
        if detected_class:
            # Update your internal data structure for the bar chart
            # For example, if you have a dict: self.detection_counts
            if not hasattr(self, 'detection_counts'):
                self.detection_counts = {}
            self.detection_counts[detected_class] = self.detection_counts.get(detected_class, 0) + 1

            # Redraw the bar chart
            self.redraw_insect_count_chart()

            # Update timeline data (if you have a structure for it)
            if not hasattr(self, 'detection_timeline'):
                self.detection_timeline = []
            self.detection_timeline.append((detection.get('timestamp'), detected_class))
            self.redraw_detection_timeline_chart()

    def redraw_insect_count_chart(self):
        # Example: clear and redraw the bar chart with updated self.detection_counts
        # (You may need to store the Figure and Axes as self attributes)
        pass

    def redraw_detection_timeline_chart(self):
        # Example: clear and redraw the timeline chart with updated self.detection_timeline
        pass

if __name__ == "__main__":
    app = vespcvGUI()
    app.mainloop()
    