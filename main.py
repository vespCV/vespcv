from src.core.logger import configure_logger, start_temperature_logging
from src.core.config_loader import load_config
from src.gui.app import vespcvGUI

def main():
    # Load configuration
    config = load_config()
    
    # Configure logging
    configure_logger(config['log_file_path'])
    start_temperature_logging()
    
    # Create and run GUI
    app = vespcvGUI()
    app.mainloop()

if __name__ == "__main__":
    main()