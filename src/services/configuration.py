import yaml
import logging

_file_path = 'config.yaml'

config = None
config_ble = None

if config is None:
    with open(_file_path, 'r') as f:
        config = yaml.safe_load(f)
        config_ble = config['ble']
        logging.debug('Configuration loaded successfully.')
