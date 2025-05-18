import logging
import logging
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    while True:
        temperature = get_cpu_temperature()
        if temperature is not None:
            logger.info("CPU Temperature: %.2f °C", temperature)
        time.sleep(900)  # Sleep for 15 minutes

def start_temperature_logging():
    """Start the temperature logging in a separate thread."""
    temp_thread = threading.Thread(target=log_temperature)
    temp_thread.daemon = True  # Daemonize thread
    temp_thread.start()