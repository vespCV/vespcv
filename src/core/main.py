from src.core.logger import configure_logger, start_temperature_logging, logger
from src.core.config_loader import load_config
from src.core.detector import DetectionController
from src.gui.app import vespcvGUI

def initialize_application():
    """Initialize all core components of the application."""
    try:
        # Load configuration
        config = load_config()
        
        # Configure logging
        configure_logger(config['log_file_path'])
        start_temperature_logging()
        
        logger.info("Application initialized successfully")
        return config
    except Exception as e:
        logger.critical(f"Failed to initialize application: {e}")
        raise

def main():
    """Main entry point for the application."""
    try:
        # Initialize core components
        config = initialize_application()
        
        # Create and run GUI
        app = vespcvGUI(config)
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()