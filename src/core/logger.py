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
        
        # Log detailed status
        if not ssh_status:
            logger.warning("SSH service is not active")
        if not port_status:
            logger.warning("SSH port is not listening")
            
        return {
            'service_active': ssh_status,
            'port_listening': port_status,
            'overall_status': ssh_status and port_status
        }
    except Exception as e:
        logger.error(f"Failed to check SSH status: {str(e)}")
        return None

def check_rpi_connect_status():
    """Check the status of the Raspberry Pi connection using rpi-connect."""
    try:
        # First check if rpi-connect command exists
        if not os.path.exists('/usr/bin/rpi-connect'):
            logger.error("rpi-connect command not found")
            return "Error: rpi-connect not installed"
            
        # Check rpi-connect status
        result = subprocess.run(['rpi-connect', 'status'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)  # Add timeout to prevent hanging
        
        if result.returncode == 0:
            status = result.stdout.strip()
            logger.debug(f"rpi-connect status: {status}")
            return status
        else:
            error_msg = result.stderr.strip()
            logger.error(f"Failed to get rpi-connect status: {error_msg}")
            return f"Error: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error("rpi-connect status check timed out")
        return "Error: Status check timed out"
    except FileNotFoundError:
        logger.error("rpi-connect command not found")
        return "Error: rpi-connect not installed"
    except Exception as e:
        logger.error(f"Exception while checking rpi-connect status: {str(e)}")
        return f"Error: {str(e)}"

def log_system_stats():
    """Log system statistics (temperature, disk usage) every 5 minutes."""
    try:
        # Ensure the logs directory exists
        os.makedirs('data/logs', exist_ok=True)
        
        with open('data/logs/system_stats.log', 'a') as stats_file:
            while True:
                try:
                    # Get temperature
                    temperature = get_cpu_temperature()
                    
                    # Get disk usage
                    disk_usage = get_disk_usage()
                    
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
                    
                    # Write to log file without SSH status
                    stats_file.write(log_entry + "\n")
                    stats_file.flush()
                    
                    # Log to console for monitoring
                    if temperature is not None:
                        logger.info("CPU Temperature: %.2f °C", temperature)
                    if disk_usage is not None:
                        logger.info("Disk Usage: %.2f GB used, %.2f GB free (%.1f%%)", 
                                  disk_usage['used_gb'], disk_usage['free_gb'], disk_usage['used_percent'])
                    
                except Exception as e:
                    logger.error(f"Error collecting system stats: {str(e)}")
                
                # Use a more reliable sleep mechanism
                for _ in range(300):  # 5 minutes = 300 seconds
                    time.sleep(1)
                    if not threading.current_thread().is_alive():
                        return
                        
    except Exception as e:
        logger.error(f"Fatal error in system stats logging: {str(e)}")
        raise

def start_temperature_logging():
    """Start the system statistics logging in a separate thread."""
    try:
        # Create header in log file if it doesn't exist
        if not os.path.exists('data/logs/system_stats.log') or os.path.getsize('data/logs/system_stats.log') == 0:
            with open('data/logs/system_stats.log', 'w') as stats_file:
                stats_file.write("timestamp,temperature_c,disk_used_gb,disk_free_gb,disk_used_percent,ssh_status\n")
        
        # Create and start the stats thread
        stats_thread = threading.Thread(target=log_system_stats, name="SystemStatsThread")
        stats_thread.daemon = True  # Make thread daemon so it exits when main program exits
        stats_thread.start()
        
        logger.info("System stats logging thread started")
        return stats_thread
    except Exception as e:
        logger.error(f"Failed to start temperature logging: {str(e)}")
        return None

def main():
    """Main function to start temperature logging."""
    try:
        configure_logger('data/logs/system.log')
        stats_thread = start_temperature_logging()
        
        if stats_thread is None:
            logger.error("Failed to start system stats logging")
            return
            
        # Keep the main thread alive and handle shutdown gracefully
        try:
            while stats_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            logger.info("Shutting down system stats logging")
            
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()

logger.info("Test log entry to check logging functionality.")

def restart_services():
    """Restart SSH and rpi-connect services and log the actions."""
    try:
        with open('data/logs/detector.log', 'a') as log_file:
            # Restart SSH service
            try:
                subprocess.run(['sudo', 'systemctl', 'restart', 'ssh'], check=True)
                logger.info("SSH service restarted successfully")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - SSH service restarted successfully\n")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to restart SSH service: {str(e)}")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to restart SSH service: {str(e)}\n")
            
            # Check SSH status after restart
            ssh_status = check_ssh_connection()
            if ssh_status and ssh_status['overall_status']:
                logger.info("SSH service is active after restart")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - SSH service is active after restart\n")
            else:
                logger.warning("SSH service is not active after restart")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - SSH service is not active after restart\n")
            
            # Restart rpi-connect service
            try:
                subprocess.run(['rpi-connect', 'on'], check=True)
                logger.info("rpi-connect service restarted successfully")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - rpi-connect service restarted successfully\n")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to restart rpi-connect service: {str(e)}")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to restart rpi-connect service: {str(e)}\n")
            
            # Check rpi-connect status after restart
            rpi_status = check_rpi_connect_status()
            if rpi_status and rpi_status != "Error retrieving status":
                logger.info(f"rpi-connect service is active after restart: {rpi_status}")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - rpi-connect service is active after restart: {rpi_status}\n")
            else:
                logger.warning("rpi-connect service is not active after restart")
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - rpi-connect service is not active after restart\n")
        
    except Exception as e:
        logger.error(f"Failed to restart services: {str(e)}")
        with open('data/logs/detector.log', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to restart services: {str(e)}\n") 