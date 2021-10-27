#!/usr/bin/env python3
from src.bluetooth.services.device_identity_service import DeviceIdentityService
from src.services.configuration import config, config_ble
from src.services import BleService, StatusIndicatorService
from src.utils.colors import VIOLET
import logging


def main():
    logging.getLogger().setLevel(level=config['logging_level'])
    logging.info('Version: ' + config['version'])

    ble = BleService(config_ble['device_name'])
    ble.start_advertising([
        DeviceIdentityService(config['device_uuid'])
    ])

    status_indicator_service = StatusIndicatorService(config['status_indicator'])
    status_indicator_service.fill(VIOLET)

    logging.info('Hit ENTER to stop the program')
    input()

    ble.stop_advertising()


if __name__ == '__main__':
    main()
