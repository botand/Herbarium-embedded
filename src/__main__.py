#!/usr/bin/env python3
from src.bluetooth.services.device_identity_service import DeviceIdentityService
from src.services.configuration import config, config_ble
from src.services.ble_service import BleService
import logging


def main():
    logging.getLogger().setLevel(level=config['logging_level'])
    logging.info('Version: ' + config['version'])

    ble = BleService('Herbariun')
    ble.start_advertising([
        DeviceIdentityService(config['device_uuid'])
    ])

    logging.info('Hit ENTER to stop the program')
    input()

    ble.stop_advertising()


if __name__ == '__main__':
    main()
