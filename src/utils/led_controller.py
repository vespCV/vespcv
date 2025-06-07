"""
LED Controller module for managing LED operations in the vespCV application.
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

class LEDController:
    def __init__(self, simulation_mode=False):
        """Initialize the LED controller.
        
        Args:
            simulation_mode (bool): If True, GPIO operations are simulated
        """
        self.config = load_config()
        self.pin = self.config['led']['pin']
        self.on_duration = self.config['led']['on_duration']
        self.last_detection_time = 0
        self.simulation_mode = simulation_mode or not GPIO_AVAILABLE
        self._is_on = False
        self.enabled = False  # Only allow GPIO activation if enabled is True
        self._lock = Lock()
        self._last_on_time = 0

        logger.info(f"LEDController initialized with on_duration={self.on_duration} seconds (simulation: {self.simulation_mode})")
        
        if not self.simulation_mode:
            self._setup_gpio()
        
    def _setup_gpio(self):
        """Set up GPIO for LED control."""
        if not GPIO_AVAILABLE:
            logger.warning("Cannot setup GPIO - RPi.GPIO module not available")
            self.simulation_mode = True
            return
            
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.OUT)
            logger.info("LED GPIO setup completed")
        except Exception as e:
            logger.error(f"Failed to setup LED GPIO: {e}")
            self.simulation_mode = True
            raise
            
    def set_enabled(self, enabled: bool):
        """Enable or disable GPIO activation."""
        self.enabled = enabled
        if not enabled:
            self.turn_off()  # Always turn off if disabling
        logger.info(f"LEDController enabled set to {self.enabled}")

    def turn_on(self):
        """Turn on the LED."""
        if not self.enabled:
            return
            
        try:
            if not self.simulation_mode and GPIO_AVAILABLE:
                GPIO.output(self.pin, GPIO.HIGH)
            self._last_on_time = time.time()
            self._is_on = True
            logger.debug(f"LED turned on, will turn off after {self.on_duration} seconds")
        except Exception as e:
            logger.error(f"Error turning on LED: {e}")
            
    def turn_off(self):
        """Turn off the LED."""
        try:
            if not self.simulation_mode and GPIO_AVAILABLE:
                GPIO.output(self.pin, GPIO.LOW)
            self._is_on = False
            logger.debug("LED turned off")
        except Exception as e:
            logger.error(f"Error turning off LED: {e}")
            
    def get_status(self):
        """Get the current LED status."""
        if not self.enabled or not self._is_on:
            return False
        return time.time() - self._last_on_time < self.on_duration
        
    def check_and_turn_off(self):
        """Check if LED should be turned off based on duration."""
        if self._is_on and time.time() - self._last_on_time >= self.on_duration:
            self.turn_off()
                
    def handle_detection(self):
        """Handle a detection event by turning on the LED."""
        if self.enabled:
            self.turn_on()
            
    def cleanup(self):
        """Clean up GPIO resources."""
        if not self.simulation_mode and GPIO_AVAILABLE:
            try:
                self.turn_off()  # Ensure LED is off before cleanup
                GPIO.cleanup(self.pin)
                logger.info("LED GPIO cleanup completed")
            except Exception as e:
                logger.error(f"Error during LED GPIO cleanup: {e}") 