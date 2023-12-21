import os
import yaml
import logging


def load_yaml_file(filename):
    """
    Load data from a YAML file.

    Args:
    filename (str): The path to the YAML file.

    Returns:
    dict: The data loaded from the YAML file.
    """
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)

        return data

    except Exception as e:
        logging.error(f'Load yaml file: {e}')
        return None


cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

config = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))
os.makedirs(name=os.path.join(cwd, config['logs_dir']), exist_ok=True)

# Configure logging
logging.basicConfig(
                    filename=os.path.join(
                        cwd, config['logs_dir'], 'client.log'
                        ),
                    level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
