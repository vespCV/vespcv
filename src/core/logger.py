import logging
import os
import shutil
import threading
import time
import subprocess
import socket
from datetime import datetime

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

def check_ssh_connection():
    """Check if SSH service is running and accepting connections."""
    try:
        # Check if SSH service is running
        result = subprocess.run(['systemctl', 'is-active', 'ssh'], 
                              capture_output=True, text=True)
        ssh_status = result.stdout.strip() == 'active'
        
        # Check if SSH port is listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 22))
        sock.close()
        port_status = result == 0
        
        return {
            'service_active': ssh_status,
            'port_listening': port_status,
            'overall_status': ssh_status and port_status
        }
    except Exception as e:
        logger.error("Failed to check SSH status: %s", e)
        return None

def check_raspberry_pi_connection():
    """Check connectivity to Raspberry Pi."""
    # This function can be removed entirely
    pass  # Remove this function

def log_system_stats():
    """Log system statistics (temperature, disk usage, and connections) every 5 minutes."""
    with open('data/logs/system_stats.log', 'a') as stats_file:
        while True:
            # Get temperature
            temperature = get_cpu_temperature()
            
            # Get disk usage
            disk_usage = get_disk_usage()
            
            # Get connection status
            ssh_status = check_ssh_connection()
            # Remove the call to check_raspberry_pi_connection
            # rpi_status = check_raspberry_pi_connection()  # Remove this line
            
            # Prepare log entry
            timestamp = time.time()
            readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{readable_time},"
            
            if temperature is not None:
                log_entry += f"{temperature:.2f},"
            else:
                log_entry += "N/A,"
                
            if disk_usage is not None:
                log_entry += f"{disk_usage['used_gb']:.2f},{disk_usage['free_gb']:.2f},{disk_usage['used_percent']:.1f},"
            else:
                log_entry += "N/A,N/A,N/A,"
            
            # Add connection status
            if ssh_status is not None:
                log_entry += f"{ssh_status['overall_status']},"
            else:
                log_entry += "N/A,"
                
            # Remove logging for Raspberry Pi connection status
            # if rpi_status is not None:
            #     log_entry += f"{rpi_status['overall_status']}"
            # else:
            #     log_entry += "N/A"
                
            # Write to log file
            stats_file.write(log_entry + "\n")
            stats_file.flush()
            
            # Log to console for monitoring
            if temperature is not None:
                logger.info("CPU Temperature: %.2f °C", temperature)
            if disk_usage is not None:
                logger.info("Disk Usage: %.2f GB used, %.2f GB free (%.1f%%)", 
                          disk_usage['used_gb'], disk_usage['free_gb'], disk_usage['used_percent'])
            if ssh_status is not None:
                logger.info("SSH Status: %s", "Active" if ssh_status['overall_status'] else "Inactive")
            # Remove logging for Raspberry Pi connection status
            # if rpi_status is not None:
            #     logger.info("Raspberry Pi Connection: %s", "Connected" if rpi_status['overall_status'] else "Disconnected")
            
            time.sleep(300)  # Sleep for 5 minutes

def start_temperature_logging():
    """Start the system statistics logging in a separate thread."""
    # Create header in log file if it doesn't exist
    if not os.path.exists('data/logs/system_stats.log') or os.path.getsize('data/logs/system_stats.log') == 0:
        with open('data/logs/system_stats.log', 'w') as stats_file:
            stats_file.write("timestamp,temperature_c,disk_used_gb,disk_free_gb,disk_used_percent,ssh_status,rpi_status\n")
    
    stats_thread = threading.Thread(target=log_system_stats)
    stats_thread.daemon = True  
    stats_thread.start()

def main():
    """Main function to start temperature logging."""
    configure_logger('data/logs/system.log') 
    start_temperature_logging()  
    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("System statistics logging stopped.")

if __name__ == "__main__":
    main() 