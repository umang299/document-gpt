import os
import logging

from .config import CONFIG_PATH, CWD
from .utils import load_yaml_file

config = load_yaml_file(filename=CONFIG_PATH)
os.makedirs(name=os.path.join(CWD, config['LOG_DIR']), exist_ok=True)

# Configure logging
logging.basicConfig(
                    filename=os.path.join(
                        CWD, config['LOG_DIR'], 'client.log'
                        ),
                    level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
