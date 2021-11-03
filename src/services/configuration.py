"""Load the configuration file"""
import os
import logging
import yaml

# pylint: disable=invalid-name

_file_path = os.environ['CONFIG_YAML_FILE']

config = None
config_ble = None

if config is None:
    with open(_file_path, 'r') as f:
        config = yaml.safe_load(f)
        config_ble = config['ble']
        logging.debug('Configuration loaded successfully.')
