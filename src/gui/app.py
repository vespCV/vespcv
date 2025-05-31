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
                
                # Resize image
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

class vespcvGUI(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.title("Aziatisch-/Geelpotige Hoornaar Detector")
        self.geometry("1024x768")
        self.configure(bg="#FFF8E1") # Light amber background

        # Initialize detection state
        self.is_detecting = False
        self.detection_thread = None

        # Configure styles for custom buttons
        style = ttk.Style()
        style.configure('Red.TButton', background='red', foreground='black')
        style.configure('Orange.TButton', background='orange', foreground='black')
        style.configure('Green.TButton', background='green', foreground='black')

        # Initialize components
        self._init_components()
        
        # Initialize detection controller
        self.detector = DetectionController(self.handle_detection_result)
        
        # Start detection on launch
        self.start_detection()

        # Add a new attribute to store the latest image path
        self.latest_image_path = None

    def _init_components(self):
        """Initialize all GUI components."""
        # Initialize image queue and handlers
        self.image_queue = queue.Queue()
        self.logger = logging.getLogger(__name__)
        self._cleanup_handlers = []
        self.image_lock = Lock()
        self.image_handler = ImageHandler(self.logger)

        # Create GUI elements
        self.create_header()
        self.create_main_content()
        self.create_control_frame()

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
        """Create the left panel with live feed and charts."""
        # Captured Image section
        self.live_feed_frame = ttk.LabelFrame(parent_frame, text="Vastgelegde afbeelding")
        self.live_feed_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.live_feed_canvas = tk.Canvas(self.live_feed_frame, bg="gray")
        self.live_feed_canvas.pack()
        self.live_feed_frame.bind('<Configure>', self.on_live_feed_frame_resize)

        # Combined charts section
        self.charts_frame = ttk.LabelFrame(parent_frame, text="Detection Statistics")
        self.charts_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.redraw_combined_chart()

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
        """Start the detection process."""
        if not self.is_detecting:
            self.is_detecting = True
            self.detector.start()
            self.logger.info("Detection started")

    def stop_detection(self):
        """Stop the detection process."""
        if self.is_detecting:
            self.is_detecting = False
            self.detector.stop()
            self.logger.info("Detection stopped")

    def handle_detection_result(self, result):
        """Handle detection results from the detector."""
        # Use self.after() to update GUI elements safely
        self.after(0, self.update_gui_with_result, result)

    def update_gui_with_result(self, result):
        """Update the GUI with the latest detection result."""
        try:
            # Update live feed with annotated image
            annotated_path = result.get("annotated_path")
            if annotated_path and os.path.exists(annotated_path):
                self.latest_image_path = annotated_path
                self.update_live_feed(annotated_path)

            # Update logs
            detection = result.get("detection", {})
            detected_class = detection.get("class", "")
            confidence = detection.get("confidence", "")
            timestamp = detection.get("timestamp", "")
            
            # Format log entry based on detection status
            if detected_class == "no_detection":
                log_entry = f"{timestamp} - No detections\n"
            else:
                log_entry = (
                    f"{timestamp} - "
                    f"Class: {detected_class}, "
                    f"Confidence: {confidence}\n"
                )
            
            self.log_text.config(state='normal')
            self.log_text.insert('end', log_entry)
            self.log_text.see('end')
            self.log_text.config(state='disabled')

            # Update charts
            self._update_charts(detection)
        except Exception as e:
            self.logger.error(f"Error updating GUI: {e}")

    def _update_charts(self, detection):
        """Update the charts with new detection data."""
        detected_class = detection.get('class')
        if detected_class:
            # Update detection counts
            if not hasattr(self, 'detection_counts'):
                self.detection_counts = {}
            
            # Only increment count for actual detections
            if detected_class != "no_detection":
                self.detection_counts[detected_class] = self.detection_counts.get(detected_class, 0) + 1

            # Update timeline data
            if not hasattr(self, 'detection_timeline'):
                self.detection_timeline = []
            self.detection_timeline.append((detection.get('timestamp'), detected_class))

            # Redraw combined chart
            self.redraw_combined_chart()

    def update_live_feed(self, image_path: str) -> None:
        """Update the live feed canvas with the new image."""
        with self.image_lock:
            canvas_width = self.live_feed_canvas.winfo_width()
            canvas_height = self.live_feed_canvas.winfo_height()
            img = self.image_handler.load_and_resize_image(
                image_path,
                (canvas_width, canvas_height)
            )
            if img:
                photo = ImageTk.PhotoImage(img)
                self.live_feed_canvas.delete("all")
                self.live_feed_canvas.create_image(
                    canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=photo
                )
                self.live_feed_canvas.image = photo

    def show_captured_image(self):
        """Show the most recently captured image."""
        image_path = os.path.join(self.config['images_folder'], 'image_after_inference.jpg')
        time.sleep(0.5)  # Add a small delay to avoid file write/read race
        if os.path.exists(image_path):
            self.update_live_feed(image_path)
        else:
            self.live_feed_canvas.delete("all")
            self.live_feed_canvas.create_text(
                self.live_feed_canvas.winfo_width() // 2,
                self.live_feed_canvas.winfo_height() // 2,
                text="No image available",
                fill="white"
            )

    def __del__(self):
        """Cleanup when the GUI is destroyed."""
        for handler in self._cleanup_handlers:
            handler()
        if hasattr(self, 'detector'):
            self.detector.shutdown()

    def redraw_combined_chart(self):
        """Redraw the detection timeline chart showing counts per configured interval."""
        try:
            # Clear the existing chart
            for widget in self.charts_frame.winfo_children():
                widget.destroy()

            # Create new figure and axes
            fig, ax = plt.subplots(figsize=(6, 4))
            
            if hasattr(self, 'detection_timeline') and self.detection_timeline:
                # Convert timestamps to datetime objects and group by configured interval
                from datetime import datetime, timedelta
                from collections import defaultdict
                
                # Get interval from config
                interval_minutes = self.config.get('chart_interval', 1)
                
                # Group detections by interval and class
                interval_counts = defaultdict(lambda: {'vvel': 0, 'other': 0})
                for timestamp, class_name in self.detection_timeline:
                    if class_name != "no_detection":  # Only count actual detections
                        # Convert timestamp to datetime
                        dt = datetime.strptime(timestamp, "%Y%m%d-%H%M%S")
                        # Round down to nearest interval
                        minutes = dt.hour * 60 + dt.minute
                        interval_start = minutes - (minutes % interval_minutes)
                        interval_key = f"{interval_start // 60:02d}:{interval_start % 60:02d}"
                        
                        # Count vvel (class 3) separately
                        if class_name == 'vvel':
                            interval_counts[interval_key]['vvel'] += 1
                        else:
                            interval_counts[interval_key]['other'] += 1
                
                # Sort by time
                sorted_intervals = sorted(interval_counts.keys())
                
                # Prepare data for stacked bar chart
                vvel_counts = [interval_counts[interval]['vvel'] for interval in sorted_intervals]
                other_counts = [interval_counts[interval]['other'] for interval in sorted_intervals]
                
                # Create stacked bar chart
                bars_vvel = ax.bar(sorted_intervals, vvel_counts, color='#FF0000', alpha=0.7, label='Vespa velutina')
                bars_other = ax.bar(sorted_intervals, other_counts, bottom=vvel_counts, color='#808080', alpha=0.7, label='Other species')
                
                # Add count labels on top of bars
                for i, (vvel, other) in enumerate(zip(vvel_counts, other_counts)):
                    total = vvel + other
                    if total > 0:  # Only add label if there are detections
                        ax.text(i, total, f'{total}',
                                ha='center', va='bottom')
                
                ax.set_xlabel(f'Time (HH:MM) - {interval_minutes} min intervals')
                ax.set_ylabel('Number of Detections')
                ax.set_title(f'Detections per {interval_minutes} Minute{"s" if interval_minutes > 1 else ""}')
                
                # Add legend
                ax.legend(loc='upper right')
                
                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45, ha='right')
                
                # Add grid for better readability
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
            else:
                # Show empty chart with message
                ax.text(0.5, 0.5, 'No detection data yet', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes)

            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
            
        except Exception as e:
            self.logger.error(f"Error redrawing timeline chart: {e}")

    def on_live_feed_frame_resize(self, event):
        # Step 3: Calculate largest 4:3 rectangle
        frame_width = event.width
        frame_height = event.height
        aspect = 4 / 3

        if frame_width / aspect <= frame_height:
            new_width = frame_width
            new_height = int(frame_width / aspect)
        else:
            new_height = frame_height
            new_width = int(frame_height * aspect)

        # Step 4: Resize canvas
        self.live_feed_canvas.config(width=new_width, height=new_height)

        # Step 5: Redraw image
        if self.latest_image_path:
            self.update_live_feed(self.latest_image_path)

if __name__ == "__main__":
    app = vespcvGUI()
    app.mainloop()
    