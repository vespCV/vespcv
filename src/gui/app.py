import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import scrolledtext # Import scrolledtext for a text area with a scrollbar

class vespcvGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vespa velutina Flitser")
        self.geometry("1024x768")
        self.configure(bg="#FFF8E1") # Light amber background

        # Configure a style for a red button
        style = ttk.Style()
        style.configure('TachtigRed.TButton', background='red', foreground='black') # Configure style for red background

        # Call methods to create different parts of the GUI
        self.create_header()
        self.create_main_content()
        self.create_control_frame()
        # We will add log frame later

    def create_header(self):
        # This method will create the header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Add the main title
        ttk.Label(header_frame, text="Aziatische Hoornaar Flitskast", font=("Arial", 24, "bold")).pack(side=tk.LEFT, expand=True)

        # Add placeholder buttons for settings (using symbols for now)
        # You can replace these with icons later if needed
        ttk.Button(header_frame, text="⚙").pack(side=tk.RIGHT, padx=2) # General Settings
        ttk.Checkbutton(header_frame, text="Bluetooth").pack(side=tk.RIGHT, padx=2) # Bluetooth toggle - consider if needed in header
        ttk.Checkbutton(header_frame, text="HDMI").pack(side=tk.RIGHT, padx=2) # HDMI toggle - consider if needed in header
        ttk.Button(header_frame, text="UITZETTEN", style='TachtigRed.TButton').pack(side=tk.RIGHT, padx=2) # Detection Settings (based on your v0_gui)
        # Add other icons/buttons from your image if desired

    def create_main_content(self):
        # This method will create the main area with live feed, detections, and charts
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create left and right frames within the main frame
        # Pack right frame first to see if it influences space allocation
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5) # Add some padding

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5) # Add some padding between left and right

        # Now we need methods to populate these frames
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent_frame):
        # This method will contain the Captured Image and Charts

        # Captured Image section (takes up the top part of the left panel)
        live_feed_frame = ttk.LabelFrame(parent_frame, text="Captured Image")
        live_feed_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Placeholder for the captured image display (using a Canvas)
        self.live_feed_canvas = tk.Canvas(live_feed_frame, bg="gray") # Store reference for updating later
        self.live_feed_canvas.pack(expand=True, fill=tk.BOTH)

        # Charts section (takes up the bottom part of the left panel)
        charts_frame = ttk.Frame(parent_frame) # Frame to hold the two charts side-by-side
        charts_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Add placeholder methods for the individual charts within the charts_frame
        self.create_insect_count_chart(charts_frame) # Bar chart
        self.create_detection_timeline_chart(charts_frame) # Line chart

    def create_insect_count_chart(self, parent_frame):
        # This method will create the Insect Detection Count bar chart
        bar_chart_frame = ttk.LabelFrame(parent_frame, text="Insect detectie teller")
        bar_chart_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5) # Pack to the left in the charts_frame

        # Create a matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(4, 3)) # Adjust figsize as needed

        # Placeholder data (replace with real data later)
        insects = ['Aziatische hoornaar', 'Europese hoornaar', 'Bij', 'Limonade wesp']
        counts = [12, 8, 5, 15]
        ax.bar(insects, counts, color='#FFA000') # Use a color that fits your scheme
        ax.set_ylabel('Count')

        # Embed the matplotlib figure in the Tkinter widget
        canvas = FigureCanvasTkAgg(fig, master=bar_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def create_detection_timeline_chart(self, parent_frame):
        # This method will create the Detection Timeline line chart
        line_chart_frame = ttk.LabelFrame(parent_frame, text="Detection Timeline")
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
        saved_detections_frame = ttk.LabelFrame(parent_frame, text="Saved Detections")
        saved_detections_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5) # Saved Detections will take up the top part of the right frame

        # Add content to the Saved Detections frame
        self.create_saved_detections_section(saved_detections_frame)

        # System Logs section (takes up the bottom part of the right panel)
        log_frame = ttk.LabelFrame(parent_frame, text="System Logs")
        log_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=5, pady=5) # Logs will take up the bottom part

        # Add placeholder method for the log display within the log_frame
        self.create_log_display(log_frame)

    def create_saved_detections_section(self, parent_frame):
        # This method will create the content inside the Saved Detections LabelFrame

        # Frame for filter and download controls
        controls_frame = ttk.Frame(parent_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        # Filter button
        ttk.Button(controls_frame, text="Asian Hornets Only").pack(side=tk.LEFT, padx=5)

        # Download button
        ttk.Button(controls_frame, text="Download").pack(side=tk.RIGHT, padx=5)

        # Frame for the detection grid placeholders
        detections_grid_frame = ttk.Frame(parent_frame)
        detections_grid_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Add 4 placeholder frames for detection entries
        for i in range(4):
            placeholder_frame = ttk.Frame(detections_grid_frame, width=100, height=120, relief='solid', borderwidth=1) # Give them a fixed size and border
            placeholder_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=2)
            # Add placeholder content inside the frame (e.g., a label or canvas)
            ttk.Label(placeholder_frame, text=f"Detection {i+1}", anchor="center").pack(expand=True, fill=tk.BOTH)

    def create_log_display(self, parent_frame):
        # This method will create the log display area
        # Using ScrolledText for a text area with a built-in scrollbar
        self.log_text = scrolledtext.ScrolledText(parent_frame, state='disabled', wrap='word') # Use state='disabled' to make it read-only
        self.log_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # We will need a mechanism to insert log messages into self.log_text later

    def create_control_frame(self):
        # This method will create the control buttons (Start/Stop Detection)
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Add Start and Stop Detection buttons
        # Removed Start Detection button as per PRD for auto-start on boot
        ttk.Button(control_frame, text="Start Detection").pack(side=tk.LEFT, padx=5) # Kept for debugging
        ttk.Button(control_frame, text="Stop Detection").pack(side=tk.LEFT, padx=5)

    # We will add a method for the log frame later

if __name__ == "__main__":
    app = vespcvGUI()
    app.mainloop()
    