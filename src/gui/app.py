import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class vespcvGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vespa velutina Flitser")
        self.geometry("1024x768")
        self.configure(bg="#FFF8E1") # Light amber background

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
        ttk.Button(header_frame, text="⚙").pack(side=tk.RIGHT, padx=2) # Detection Settings (based on your v0_gui)
        # Add other icons/buttons from your image if desired

    def create_main_content(self):
        # This method will create the main area with live feed, detections, and charts
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create left and right frames within the main frame
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5) # Add some padding between left and right

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5) # Add some padding

        # Now we need methods to populate these frames
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent_frame):
        # This method will contain the Live Feed and Charts

        # Live Feed section (takes up the top part of the left panel)
        live_feed_frame = ttk.LabelFrame(parent_frame, text="Live Feed")
        live_feed_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Placeholder for the live feed display (using a Canvas)
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
        pass # Placeholder

    def create_right_panel(self, parent_frame):
        # This method will contain Saved Detections and Harp Control / Logs
        saved_detections_frame = ttk.LabelFrame(parent_frame, text="Saved Detections")
        saved_detections_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5) # Saved Detections will take up the top part of the right frame

        # We will add the log/harp control frame below this one later

    def create_control_frame(self):
        # This method will create the control buttons (Start/Stop Detection)
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        pass # Placeholder

    # We will add a method for the log frame later

if __name__ == "__main__":
    app = vespcvGUI()
    app.mainloop()
    