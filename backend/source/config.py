import os
import sys

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)

CONFIG_PATH = os.path.join(cwd, 'config.yaml')
CONV_DIR = os.path.join(cwd, 'conversations')
DB_DIR = os.path.join(cwd, 'storage')
CWD = cwd
