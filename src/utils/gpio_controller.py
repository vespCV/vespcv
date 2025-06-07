"""
GPIO Controller module for managing GPIO operations in the vespCV application.
"""
import time
import logging
from threading import Lock

from src.core.logger import logger
from src.core.config_loader import load_config

# Try to import RPi.GPIO, if not available, set to None
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO = None
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO module not available. Running in simulation mode only.")

logger = logging.getLogger(__name__)

class GPIOController:
    def __init__(self):
        """Initialize the GPIO controller."""
        self.config = load_config()
        self.pin = self.config['led']['pin']  # Keep the key as 'led' for now
        self.on_duration = self.config['led']['on_duration']  # Keep the key as 'led' for now
        self._is_on = False
        self.enabled = False  # Only allow GPIO activation if enabled is True
        self._lock = Lock()
        self._last_on_time = 0

        logger.info(f"GPIOController initialized with on_duration={self.on_duration} seconds")
        
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Set up GPIO for control."""
        if not GPIO_AVAILABLE:
            logger.warning("Cannot setup GPIO - RPi.GPIO module not available")
            return
            
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.OUT)
            logger.info("GPIO setup completed")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {e}")
            raise
            
    def set_enabled(self, enabled: bool):
        """Enable or disable GPIO activation."""
        self.enabled = enabled
        if not enabled:
            self.turn_off()  # Always turn off if disabling
        logger.info(f"GPIOController enabled set to {self.enabled}")

    def turn_on(self):
        """Turn on the GPIO."""
        if not self.enabled:
            return
            
        try:
            if GPIO_AVAILABLE:
                GPIO.output(self.pin, GPIO.HIGH)
            self._last_on_time = time.time()
            self._is_on = True
            logger.debug(f"GPIO turned on, will turn off after {self.on_duration} seconds")
        except Exception as e:
            logger.error(f"Error turning on GPIO: {e}")
            
    def turn_off(self):
        """Turn off the GPIO."""
        try:
            if GPIO_AVAILABLE:
                GPIO.output(self.pin, GPIO.LOW)
            self._is_on = False
            logger.debug("GPIO turned off")
        except Exception as e:
            logger.error(f"Error turning off GPIO: {e}")
            
    def get_status(self):
        """Get the current GPIO status."""
        if not self.enabled or not self._is_on:
            return False
        return time.time() - self._last_on_time < self.on_duration
        
    def check_and_turn_off(self):
        """Check if GPIO should be turned off based on duration."""
        if self._is_on and time.time() - self._last_on_time >= self.on_duration:
            self.turn_off()
                
    def handle_detection(self):
        """Handle a detection event by turning on the GPIO."""
        if self.enabled:
            self.turn_on()
            
    def cleanup(self):
        """Clean up GPIO resources."""
        if GPIO_AVAILABLE:
            try:
                self.turn_off()  # Ensure GPIO is off before cleanup
                GPIO.cleanup(self.pin)
                logger.info("GPIO cleanup completed")
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}") 
