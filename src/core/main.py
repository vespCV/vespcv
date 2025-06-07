import os

from src.core.config_loader import load_config
from src.core.detector import DetectionController
from src.core.logger import configure_logger, start_temperature_logging, logger
from src.gui.app import vespcvGUI

def create_directories(required_dirs):
    """Create necessary directories if they do not exist."""
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)  # Create directory if it doesn't exist
        print(f"Created directory: {dir_path}")  # Log the creation of the directory

def initialize_application():
    """Initialize all core components of the application."""
    try:
        # Load configuration
        config = load_config()
        
        # Create necessary directories first, before any logging
        required_dirs = [
            os.path.dirname(config['log_file_path']),  # Create logs directory
            config['images_folder'],                   # Create images directory
            'data/yolo_jpg_txt'                       # Create yolo directory
        ]
        
        create_directories(required_dirs)
        
        # Now that directories exist, configure logging
        configure_logger(config['log_file_path'])
        start_temperature_logging()
        
        logger.info("Application initialized successfully")
        return config
    except Exception as e:
        print(f"Failed to initialize application: {e}")  # Use print instead of logger
        raise

def main():
    """Main entry point for the application."""
    try:
        # Initialize core components
        config = initialize_application()
        
        # Create and run GUI
        app = vespcvGUI(config)
        
        # Set up proper shutdown handling
        def on_closing():
            try:
                logger.info("Starting application shutdown...")
                
                # Stop detection if running
                if app.is_detecting:
                    logger.info("Stopping detection...")
                    app.stop_detection()
                
                # Shutdown detector
                if hasattr(app, 'detector'):
                    logger.info("Shutting down detector...")
                    app.detector.shutdown()
                
                # Clean up any remaining resources
                logger.info("Cleaning up resources...")
                for handler in app._cleanup_handlers:
                    handler()
                
                # Destroy the window and quit
                logger.info("Destroying window...")
                app.destroy()
                
                # Force quit the application
                logger.info("Quitting application...")
                app.quit()
                
                # Exit the process
                import sys
                sys.exit(0)
            except Exception as e:
                logger.critical(f"Error during application shutdown: {e}")
                # Force quit even if there's an error
                app.quit()
                sys.exit(1)
        
        # Set the protocol handler
        app.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the main loop
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()