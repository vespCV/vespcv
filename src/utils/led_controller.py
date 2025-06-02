"""
LED Controller module for managing LED operations in the vespCV application.
"""

import time
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
        self.is_on = False
        self.enabled = False  # Only allow GPIO activation if enabled is True
        
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

    def handle_detection(self):
        """Handle LED control for a new detection."""
        if not self.enabled:
            logger.info("Detection ignored: GPIO not enabled.")
            return
        current_time = time.time()
        self.turn_on()
        self.last_detection_time = current_time
        logger.info(f"LED turned on due to detection (simulation: {self.simulation_mode}, on_duration={self.on_duration})")
            
    def check_and_turn_off(self):
        """Check if LED should be turned off based on time since last detection."""
        if not self.enabled:
            self.turn_off()
            return
        current_time = time.time()
        time_since_detection = current_time - self.last_detection_time
        if self.is_on and time_since_detection >= self.on_duration:
            self.turn_off()
            logger.info(f"LED turned off after {time_since_detection:.1f} seconds (simulation: {self.simulation_mode}, on_duration={self.on_duration})")
            
    def turn_on(self):
        if not self.enabled:
            self.is_on = False
            if not self.simulation_mode and GPIO_AVAILABLE:
                GPIO.output(self.pin, GPIO.LOW)
            logger.info("turn_on() called but GPIO not enabled; LED remains OFF")
            return
        if not self.is_on:
            self.is_on = True
            if self.simulation_mode:
                logger.info("Simulated: LED ON")
            else:
                try:
                    GPIO.output(self.pin, GPIO.HIGH)
                    logger.info("LED turned ON (GPIO activated)")
                except Exception as e:
                    logger.error(f"Failed to turn on LED: {e}")
                    self.simulation_mode = True
        
    def turn_off(self):
        if self.is_on or not self.enabled:
            was_on = self.is_on  # Store the previous state
            self.is_on = False
            if self.simulation_mode:
                if was_on:  # Only log if the LED was actually on
                    logger.info("Simulated: LED OFF")
            else:
                try:
                    GPIO.output(self.pin, GPIO.LOW)
                    if was_on:  # Only log if the LED was actually on
                        logger.info("LED turned OFF (GPIO deactivated)")
                except Exception as e:
                    logger.error(f"Failed to turn off LED: {e}")
                    self.simulation_mode = True
        
    def cleanup(self):
        """Clean up GPIO resources."""
        if not self.simulation_mode and GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                logger.info("LED GPIO cleanup completed")
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}")
        else:
            logger.info("LED simulation cleanup completed")
        self.is_on = False
        self.enabled = False
        
    def get_status(self):
        """Get the current LED status (True if GPIO is enabled and LED is ON)."""
        status = self.is_on and self.enabled
        logger.debug(f"LED status: {status} (enabled: {self.enabled}, simulation: {self.simulation_mode})")
        return status 