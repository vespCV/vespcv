import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import scrolledtext # Import scrolledtext for a text area with a scrollbar
import threading
import time
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import queue
import logging
from threading import Lock
from typing import Optional, List, Dict
import numpy as np
from src.core.detector import DetectionController
from src.utils.led_controller import LEDController
from datetime import datetime, timedelta

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
        style.configure('LED.TButton', background='gray', foreground='black')

        # Initialize LED controller in simulation mode
        self.led_controller = LEDController(simulation_mode=True)
        
        # Initialize components
        self._init_components()
        
        # Initialize detection controller with our LED controller
        self.detector = DetectionController(self.handle_detection_result, self.led_controller)
        
        # Start detection on launch
        self.start_detection()

        # Add a new attribute to store the latest image path
        self.latest_image_path = None
        
        # Start LED status update
        self._update_led_status()

        # Start LED timer
        self._start_led_timer()

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
        
        # Create LED control frame
        led_frame = ttk.Frame(header_frame)
        led_frame.pack(side=tk.RIGHT, padx=10)
        
        # Create LED indicator
        self.led_indicator = ttk.Label(led_frame, text="●", font=("Arial", 24))
        self.led_indicator.pack(side=tk.LEFT, padx=5)
        self._update_led_indicator()
        
        # Create LED toggle button
        self.led_button = ttk.Button(led_frame, text="GPIO", style='LED.TButton', 
                                   command=self.toggle_led_control)
        self.led_button.pack(side=tk.LEFT, padx=5)
        
        # Create detection control buttons
        ttk.Button(header_frame, text="STOP DETECTIE", style='Orange.TButton', 
                  command=self.stop_detection).pack(side=tk.RIGHT, padx=2)
        ttk.Button(header_frame, text="START DETECTIE", style='Green.TButton', 
                  command=self.start_detection).pack(side=tk.RIGHT, padx=2)

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
        interval_minutes = self.config.get('chart_interval', 1)
        self.charts_frame = ttk.LabelFrame(
            parent_frame,
            text=f'Detecties per {interval_minutes} Minute{"s" if interval_minutes > 1 else ""}'
        )
        self.charts_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.redraw_combined_chart()

    def create_right_panel(self, parent_frame):
        # This method will contain Saved Detections and Logs

        # Saved Detections section (takes up the top part of the right panel)
        self.saved_detections_frame = ttk.LabelFrame(parent_frame, text="Opgeslagen detecties")
        self.saved_detections_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.create_saved_detections_section(self.saved_detections_frame)

        # System Logs section (takes up the bottom part of the right panel)
        log_frame = ttk.LabelFrame(parent_frame, text="Detectie log")
        log_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5) # Logs will take up the bottom part

        # Add placeholder method for the log display within the log_frame
        self.create_log_display(log_frame)

    def create_saved_detections_section(self, parent_frame):
        """This method will create the content inside the Saved Detections LabelFrame"""
        
        # Frame for the detection grid placeholders
        detections_grid_frame = ttk.Frame(parent_frame)
        detections_grid_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Load images that start with "vvel"
        images_folder = '/home/vcv/vespcv/data/images'
        os.makedirs(images_folder, exist_ok=True)
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

        num_real = len(top_images)
        num_placeholders = 4 - num_real

        # Add image frames to the grid
        for i, (image_name, _, time_part) in enumerate(top_images):
            image_path = os.path.join(images_folder, image_name)
            try:
                img = Image.open(image_path)
                img.thumbnail((120, 90))
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                self.logger.error(f"Failed to load thumbnail for {image_path}: {e}")
                continue

            # Create a frame for each image
            placeholder_frame = ttk.Frame(detections_grid_frame, width=100, height=120)
            placeholder_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=6)

            # Add the image to the frame
            label = ttk.Label(placeholder_frame, image=photo)
            label.image = photo  # Keep a reference to avoid garbage collection
            label.pack(expand=True, fill=tk.BOTH)
            
            # Add click event to download original image
            def create_click_handler(original_path):
                def on_click(event):
                    try:
                        # Get the original image path from yolo_jpg_txt directory
                        yolo_dir = os.path.join('data', 'yolo_jpg_txt')
                        original_filename = os.path.basename(original_path)
                        original_image_path = os.path.join(yolo_dir, original_filename)
                        
                        if os.path.exists(original_image_path):
                            # Try to use Desktop first, fallback to Downloads folder
                            home_dir = os.path.expanduser("~")
                            desktop_path = os.path.join(home_dir, "Desktop")
                            downloads_path = os.path.join(home_dir, "Downloads")
                            
                            # Create the target directory if it doesn't exist
                            target_dir = desktop_path if os.path.exists(desktop_path) else downloads_path
                            os.makedirs(target_dir, exist_ok=True)
                            
                            # Copy the original image to the target directory
                            import shutil
                            download_path = os.path.join(target_dir, original_filename)
                            shutil.copy2(original_image_path, download_path)
                            
                            # Log the download
                            self.logger.info(f"Original image downloaded to: {download_path}")
                            
                            # Show success message
                            tk.messagebox.showinfo("Download", f"Image downloaded to: {download_path}")
                        else:
                            tk.messagebox.showerror("Error", "Original image not found")
                    except Exception as e:
                        self.logger.error(f"Error downloading image: {e}")
                        tk.messagebox.showerror("Error", f"Failed to download image: {str(e)}")
                
                return on_click
            
            # Bind click event to the label
            label.bind('<Button-1>', create_click_handler(image_path))

            # Format timestamp to hh:mm:ss
            if len(time_part) == 6:
                formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
            else:
                formatted_time = time_part  # fallback

            ttk.Label(placeholder_frame, text=formatted_time, anchor="center").pack(expand=True, fill=tk.BOTH)

        # Add placeholders if there are fewer than 4 images
        for _ in range(num_placeholders):
            # Create a blank image (e.g., gray background)
            img = Image.new('RGB', (120, 90), color=(200, 200, 200))
            draw = ImageDraw.Draw(img)
            # Add text in the center
            text = "No detection"
            font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(
                ((120 - text_width) // 2, (90 - text_height) // 2),
                text, fill=(100, 100, 100), font=font
            )
            photo = ImageTk.PhotoImage(img)
            placeholder_frame = ttk.Frame(detections_grid_frame, width=100, height=120)
            placeholder_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=6)
            label = ttk.Label(placeholder_frame, image=photo)
            label.image = photo
            label.pack(expand=True, fill=tk.BOTH)
            ttk.Label(placeholder_frame, text="--:--:--", anchor="center").pack(expand=True, fill=tk.BOTH)

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
            else:
                # If no annotated image, try to show the latest captured image
                latest_capture = os.path.join(self.config['images_folder'], 'image_for_detection.jpg')
                if os.path.exists(latest_capture):
                    self.latest_image_path = latest_capture
                    self.update_live_feed(latest_capture)

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

            # Refresh saved detections
            self.refresh_saved_detections()

            # Immediately update the LED indicator after a detection
            self._update_led_indicator()
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
        try:
            with self.image_lock:
                # Get current canvas size
                canvas_width = self.live_feed_canvas.winfo_width()
                canvas_height = self.live_feed_canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    # Canvas not ready yet, schedule update for later
                    self.after(100, lambda: self.update_live_feed(image_path))
                    return
                
                # Load and resize image
                img = self.image_handler.load_and_resize_image(
                    image_path,
                    (canvas_width, canvas_height)
                )
                
                if img:
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    
                    # Clear canvas and create new image
                    self.live_feed_canvas.delete("all")
                    self.live_feed_canvas.create_image(
                        canvas_width // 2,
                        canvas_height // 2,
                        anchor=tk.CENTER,
                        image=photo
                    )
                    # Keep a reference to prevent garbage collection
                    self.live_feed_canvas.image = photo
                else:
                    # Show error message if image loading failed
                    self.live_feed_canvas.delete("all")
                    self.live_feed_canvas.create_text(
                        canvas_width // 2,
                        canvas_height // 2,
                        text="No image available",
                        fill="white",
                        font=("Arial", 14)
                    )
        except Exception as e:
            self.logger.error(f"Error updating live feed: {e}")
            # Show error message on canvas
            self.live_feed_canvas.delete("all")
            self.live_feed_canvas.create_text(
                self.live_feed_canvas.winfo_width() // 2,
                self.live_feed_canvas.winfo_height() // 2,
                text="Error updating display",
                fill="white",
                font=("Arial", 14)
            )

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
        if hasattr(self, 'led_controller'):
            self.led_controller.cleanup()

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
                from collections import defaultdict
                
                # Group detections by interval and class
                interval_counts = defaultdict(lambda: {'vvel': 0, 'other': 0})
                for timestamp, class_name in self.detection_timeline:
                    if class_name != "no_detection":  # Only count actual detections
                        # Convert timestamp to datetime
                        dt = datetime.strptime(timestamp, "%Y%m%d-%H%M%S")
                        # Round down to nearest interval
                        minutes = dt.hour * 60 + dt.minute
                        interval_start = minutes - (minutes % self.config.get('chart_interval', 1))
                        interval_key = f"{interval_start // 60:02d}:{interval_start % 60:02d}"
                        
                        # Count vvel (class 3) separately
                        if class_name == 'vvel':
                            interval_counts[interval_key]['vvel'] += 1
                        else:
                            interval_counts[interval_key]['other'] += 1
                
                # Get current interval key
                now = datetime.now()
                interval_minutes = self.config.get('chart_interval', 1)
                minutes = now.hour * 60 + now.minute
                interval_start = minutes - (minutes % interval_minutes)
                current_interval_key = f"{interval_start // 60:02d}:{interval_start % 60:02d}"

                # Ensure the current interval is present in the data
                if current_interval_key not in interval_counts:
                    interval_counts[current_interval_key] = {'vvel': 0, 'other': 0}

                # 1. Find the earliest and latest interval
                all_interval_keys = list(interval_counts.keys())
                all_interval_keys.append(current_interval_key)
                all_interval_keys = sorted(set(all_interval_keys))

                # Convert interval keys to datetime objects for range calculation
                interval_format = "%H:%M"
                interval_times = [datetime.strptime(k, interval_format) for k in all_interval_keys]
                start_time = min(interval_times)
                end_time = max(interval_times)

                # 2. Build a complete list of intervals
                num_intervals = int(((end_time - start_time).total_seconds() // 60) // interval_minutes) + 1
                full_intervals = [
                    (start_time + timedelta(minutes=i * interval_minutes)).strftime(interval_format)
                    for i in range(num_intervals)
                ]

                # 3. Fill missing intervals with zero counts
                for interval in full_intervals:
                    if interval not in interval_counts:
                        interval_counts[interval] = {'vvel': 0, 'other': 0}

                # 4. Prepare data for plotting
                sorted_intervals = full_intervals
                vvel_counts = [interval_counts[interval]['vvel'] for interval in sorted_intervals]
                other_counts = [interval_counts[interval]['other'] for interval in sorted_intervals]
                
                # Add dummy intervals for padding
                dummy_left = ''
                dummy_right = ''
                sorted_intervals = [dummy_left] + sorted_intervals + [dummy_right]
                vvel_counts = [0] + vvel_counts + [0]
                other_counts = [0] + other_counts + [0]
                
                # Create stacked bar chart
                x = np.arange(len(sorted_intervals))
                bar_width = 0.1
                bars_vvel = ax.bar(x, vvel_counts, width=bar_width, color='#FF0000', alpha=0.7, label='Vespa velutina')
                bars_other = ax.bar(x, other_counts, width=bar_width, bottom=vvel_counts, color='#808080', alpha=0.7, label='Other species')
                
                # Add count labels on top of bars
                for i, (vvel, other) in enumerate(zip(vvel_counts, other_counts)):
                    total = vvel + other
                    if total > 0:  # Only add label if there are detections
                        ax.text(i, total, f'{total}',
                                ha='center', va='bottom')
                
                ax.set_xlabel(f'Time (HH:MM) - {interval_minutes} min intervals')
                ax.set_ylabel('Number of Detections')
                # ax.set_title(f'Detecties per {interval_minutes} Minute{"s" if interval_minutes > 1 else ""}')
                
                # Add legend
                ax.legend(loc='upper right')
                
                # Rotate x-axis labels for better readability
                ax.set_xticks(x)
                ax.set_xticklabels(sorted_intervals, rotation=45, ha='right')
                
                # Add grid for better readability
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
            else:
                # Show the last N intervals, even if there are no detections yet
                now = datetime.now()
                interval_minutes = self.config.get('chart_interval', 1)
                N = 5  # Number of intervals to show (change as needed)
                interval_format = "%H:%M"

                # Build a list of the last N intervals ending with the current one
                full_intervals = [
                    (now - timedelta(minutes=(N - 1 - i) * interval_minutes)).strftime(interval_format)
                    for i in range(N)
                ]
                vvel_counts = [0] * N
                other_counts = [0] * N

                # Create stacked bar chart (all empty)
                bars_vvel = ax.bar(full_intervals, vvel_counts, color='#FF0000', alpha=0.7, label='Vespa velutina')
                bars_other = ax.bar(full_intervals, other_counts, bottom=vvel_counts, color='#808080', alpha=0.7, label='Other species')

                ax.set_xlabel(f'Time (HH:MM) - {interval_minutes} min intervals')
                ax.set_ylabel('Number of Detections')
                plural = "s" if interval_minutes > 1 else ""
                ax.set_title(f'Detections per {interval_minutes} Minute{plural}')
                ax.legend(loc='upper right')
                plt.xticks(rotation=45, ha='right')
                ax.grid(True, linestyle='--', alpha=0.3)
                plt.tight_layout()

            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
            
        except Exception as e:
            self.logger.error(f"Error redrawing timeline chart: {e}")

    def on_live_feed_frame_resize(self, event):
        """Handle live feed frame resize events."""
        try:
            # Get new frame dimensions
            frame_width = event.width
            frame_height = event.height
            
            if frame_width <= 1 or frame_height <= 1:
                return  # Ignore invalid sizes
            
            # Calculate dimensions maintaining 4:3 aspect ratio
            aspect = 4 / 3
            
            if frame_width / aspect <= frame_height:
                new_width = frame_width
                new_height = int(frame_width / aspect)
            else:
                new_height = frame_height
                new_width = int(frame_height * aspect)
            
            # Update canvas size
            self.live_feed_canvas.config(width=new_width, height=new_height)
            
            # Redraw current image if available
            if self.latest_image_path:
                self.update_live_feed(self.latest_image_path)
        except Exception as e:
            self.logger.error(f"Error handling live feed resize: {e}")

    def refresh_saved_detections(self):
        # Remove all widgets from the frame
        for widget in self.saved_detections_frame.winfo_children():
            widget.destroy()
        # Rebuild the section
        self.create_saved_detections_section(self.saved_detections_frame)

    def toggle_led_control(self):
        """Toggle between GPIO ON (red) and OFF (gray)."""
        try:
            # Toggle enabled state on the existing LEDController
            new_enabled = not self.led_controller.enabled
            self.led_controller.set_enabled(new_enabled)
            self.detector.led_controller = self.led_controller
            
            # Update button style
            if self.led_controller.enabled:
                self.led_button.configure(style='Red.TButton')  # red (GPIO ON)
                self.logger.info("GPIO ACTIVATION ON (harp armed)")
            else:
                self.led_button.configure(style='LED.TButton')  # gray (GPIO OFF)
                self.logger.info("GPIO ACTIVATION OFF (harp disarmed)")
            
            # Immediately update indicator
            self._update_led_indicator()
        except Exception as e:
            self.logger.error(f"Error toggling LED control: {e}")
            self.led_controller.set_enabled(False)
            self.detector.led_controller = self.led_controller
            self.led_button.configure(style='LED.TButton')
            self._update_led_indicator()

    def _update_led_status(self):
        """Update LED status periodically."""
        try:
            self._update_led_indicator()
        except Exception as e:
            self.logger.error(f"Error updating LED status: {e}")
        finally:
            # Schedule next update
            self.after(100, self._update_led_status)

    def _update_led_indicator(self):
        """Update the LED indicator color based on current status and GPIO enabled state."""
        try:
            status = self.led_controller.get_status()
            self.logger.debug(f"Updating LED indicator, status: {status}, enabled: {self.led_controller.enabled}")
            if status:
                self.led_indicator.configure(foreground='yellow')
            else:
                self.led_indicator.configure(foreground='gray')
        except Exception as e:
            self.logger.error(f"Error updating LED indicator: {e}")

    def _start_led_timer(self):
        """Start a periodic timer to check and turn off the LED."""
        self.led_controller.check_and_turn_off()
        self._update_led_indicator()
        self.after(500, self._start_led_timer)

if __name__ == "__main__":
    app = vespcvGUI()
    app.mainloop()
    