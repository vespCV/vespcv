import yaml

def load_config(config_path='config/config.yaml'):
    """Load the configuration from the specified YAML file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
        KeyError: If 'model_path' key is missing in the configuration.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as e:
        print(f"Error: '{config_path}' file not found.")
        raise e
    except yaml.YAMLError as e:
        print("Error: Failed to parse the YAML config file.")
        raise e

    if 'model_path' not in config:
        raise KeyError("Error: 'model_path' key is missing in the config file.")

    return config

if __name__ == "__main__":
    config = load_config() # Load the config

    # Test the config
    model_path = config['model_path']
    print(f"Model path: {model_path}")

    images_folder = config['images_folder']
    print(f"Images folder: {images_folder}")
    
    conf_threshold = config['conf_threshold']
    print(f"Confidence threshold: {conf_threshold}")

    capture_interval = config['capture_interval']
    print(f"Capture interval: {capture_interval}")