import os
import sys
import logging
from .utils import load_yaml_file

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)

config = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))[0]
os.makedirs(name=os.path.join(cwd, config['logs_dir']), exist_ok=True)

# Configure logging
logging.basicConfig(
                    filename=os.path.join(
                        cwd, config['logs_dir'], 'client.log'
                        ),
                    level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
