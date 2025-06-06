"""
Simple GPIO test script to verify RPi.GPIO installation and access.
"""

import RPi.GPIO as GPIO
import time
from src.core.logger import logger

def test_gpio():
    """Test basic GPIO functionality."""
    try:
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Test pin (using the one from config)
        from src.core.config_loader import load_config
        config = load_config()
        test_pin = config['led']['pin']
        
        logger.info(f"Testing GPIO pin {test_pin}")
        
        # Set up the pin as output
        GPIO.setup(test_pin, GPIO.OUT)
        
        # Blink the LED 3 times
        for _ in range(3):
            logger.info("LED ON")
            GPIO.output(test_pin, GPIO.HIGH)
            time.sleep(1)
            
            logger.info("LED OFF")
            GPIO.output(test_pin, GPIO.LOW)
            time.sleep(1)
            
        logger.info("GPIO test completed successfully")
        
    except Exception as e:
        logger.error(f"GPIO test failed: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_gpio() 