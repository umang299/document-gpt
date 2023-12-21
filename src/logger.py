import os
import sys
import logging

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)

# Configure logging
logging.basicConfig(
                    filename=os.path.join(cwd, 'logs', 'client.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
