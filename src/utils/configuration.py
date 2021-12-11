"""Load the configuration file"""
import os
import yaml

# pylint: disable=invalid-name

_file_path = os.getenv("CONFIG_YAML_FILE", "config.yaml")

config = None
config_ble = None

if config is None:
    with open(_file_path, "r") as f:
        config = yaml.safe_load(f)
        config_ble = config["ble"]
