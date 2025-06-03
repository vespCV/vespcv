import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def load_config(config_path='config/config.yaml') -> dict:
    """Load the configuration from the specified YAML file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
        KeyError: If any required configuration key is missing.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as e:
        logging.error(f"Error: '{config_path}' file not found.")
        raise e
    except yaml.YAMLError as e:
        logging.error("Error: Failed to parse the YAML config file.")
        raise e

    # List of required configuration keys
    required_keys = [
        'model_path',
        'images_folder',
        'log_file_path',
        'conf_threshold',
        'class_names',
        'lensposition',
        'capture_interval'
    ]

    # Validate all required keys are present
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logging.error(f"Error: Missing required configuration keys: {', '.join(missing_keys)}")
        raise KeyError(f"Error: Missing required configuration keys: {', '.join(missing_keys)}")

    # Validate specific value types and ranges
    if not isinstance(config['conf_threshold'], (int, float)) or not 0 <= config['conf_threshold'] <= 1:
        logging.error("Error: 'conf_threshold' must be a number between 0 and 1")
        raise ValueError("Error: 'conf_threshold' must be a number between 0 and 1")
    
    if not isinstance(config['lensposition'], (int, float)) or not 0 <= config['lensposition'] <= 10:
        logging.error("Error: 'lensposition' must be a number between 0.0 and 10.0")
        raise ValueError("Error: 'lensposition' must be a number between 0.0 and 10.0")
    
    if not isinstance(config['capture_interval'], (int, float)) or config['capture_interval'] <= 0:
        logging.error("Error: 'capture_interval' must be a positive number")
        raise ValueError("Error: 'capture_interval' must be a positive number")

    return config

if __name__ == "__main__":
    config = load_config()  # Load the config

    # Test the config
    logging.info("Configuration loaded successfully:")
    for key, value in config.items():
        logging.info(f"{key}: {value}")