import logging
import time
import threading

# Configure logging (initial setup without handlers)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def configure_logger(log_file_path):
    """Configure the logger to write logs to the specified file."""
    # Clear existing handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handlers
    c_handler = logging.StreamHandler() # Console handler
    f_handler = logging.FileHandler(log_file_path) # File handler

    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

def get_cpu_temperature():
    """Get the CPU temperature in Celsius."""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as file:
            temp_milli_c = int(file.read())
            return temp_milli_c / 1000.0  # Convert to Celsius
    except Exception as e:
        logger.error("Failed to read CPU temperature: %s", e)
        return None

def log_temperature():
    """Log the CPU temperature every 15 minutes."""
    with open('data/logs/system_stats.log', 'a') as stats_file:  # Open the log file
        while True:
            temperature = get_cpu_temperature()
            if temperature is not None:
                logger.info("CPU Temperature: %.2f °C", temperature)
                stats_file.write(f"{time.time()},{temperature:.2f}\n")  # Save timestamp and temperature
            time.sleep(900)  # Sleep for 15 minutes

def start_temperature_logging():
    """Start the temperature logging in a separate thread."""
    temp_thread = threading.Thread(target=log_temperature)
    temp_thread.daemon = True  # Daemonize thread
    temp_thread.start()

def main():
    """Main function to start temperature logging."""
    configure_logger('data/logs/system.log')  # Set your log file path
    start_temperature_logging()  # Start logging in a separate thread
    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Temperature logging stopped.")

if __name__ == "__main__":
    main()  # Call the main function