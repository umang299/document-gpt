import os
import sys

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)

os.makedirs(os.path.join(cwd, 'data'), exist_ok=True)

CONFIG_PATH = os.path.join(cwd, 'config.yaml')
CONV_DIR = os.path.join(cwd, 'conversations')
DB_DIR = os.path.join(cwd, 'storage')
DATA_DIR = os.path.join(cwd, 'data')
CWD = cwd
