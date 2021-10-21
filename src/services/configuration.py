import yaml
import logging

_file_path = 'config.yaml'

config = None

if config is None:
    with open(_file_path, 'r') as f:
        config = yaml.safe_load(f)
        logging.debug('Configuration loaded successfully.')
