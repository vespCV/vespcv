from ultralytics import YOLO
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


def create_model(model_path):
    """Load the YOLO model from the given model path.

    Args:
        model_path (str): The path to the pre-trained YOLO model weights.

    Returns:
        YOLO: The loaded YOLO model.

    Raises:
        Exception: If there is a failure loading the model.
    """
    try:
        model = YOLO(model_path)
    except Exception as e:
        print("Error: Failed to load YOLO model.")
        raise e
    return model


if __name__ == '__main__':
    config = load_config()
    model = create_model(config['model_path'])


