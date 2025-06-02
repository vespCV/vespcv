import logging
import time
import threading
import os
import shutil

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

def get_disk_usage():
    """Get disk usage information for the root filesystem."""
    try:
        total, used, free = shutil.disk_usage("/")
        return {
            'total_gb': total / (1024**3),  # Convert to GB
            'used_gb': used / (1024**3),
            'free_gb': free / (1024**3),
            'used_percent': (used / total) * 100
        }
    except Exception as e:
        logger.error("Failed to read disk usage: %s", e)
        return None

def log_system_stats():
    """Log system statistics (temperature and disk usage) every 15 minutes."""
    with open('data/logs/system_stats.log', 'a') as stats_file:
        while True:
            # Get temperature
            temperature = get_cpu_temperature()
            
            # Get disk usage
            disk_usage = get_disk_usage()
            
            # Prepare log entry
            timestamp = time.time()
            log_entry = f"{timestamp},"
            
            if temperature is not None:
                log_entry += f"{temperature:.2f},"
            else:
                log_entry += "N/A,"
                
            if disk_usage is not None:
                log_entry += f"{disk_usage['used_gb']:.2f},{disk_usage['free_gb']:.2f},{disk_usage['used_percent']:.1f}"
            else:
                log_entry += "N/A,N/A,N/A"
                
            # Write to log file
            stats_file.write(log_entry + "\n")
            stats_file.flush()  # Ensure immediate write to disk
            
            # Log to console for monitoring
            if temperature is not None:
                logger.info("CPU Temperature: %.2f °C", temperature)
            if disk_usage is not None:
                logger.info("Disk Usage: %.2f GB used, %.2f GB free (%.1f%%)", 
                          disk_usage['used_gb'], disk_usage['free_gb'], disk_usage['used_percent'])
            
            time.sleep(900)  # Sleep for 15 minutes

def start_temperature_logging():
    """Start the system statistics logging in a separate thread."""
    # Create header in log file if it doesn't exist
    if not os.path.exists('data/logs/system_stats.log') or os.path.getsize('data/logs/system_stats.log') == 0:
        with open('data/logs/system_stats.log', 'w') as stats_file:
            stats_file.write("timestamp,temperature_c,disk_used_gb,disk_free_gb,disk_used_percent\n")
    
    stats_thread = threading.Thread(target=log_system_stats)
    stats_thread.daemon = True  # Daemonize thread
    stats_thread.start()

def main():
    """Main function to start temperature logging."""
    configure_logger('data/logs/system.log')  # Set your log file path
    start_temperature_logging()  # Start logging in a separate thread
    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("System statistics logging stopped.")

if __name__ == "__main__":
    main()  # Call the main function