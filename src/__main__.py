#!/usr/bin/env python3
import sys

from src.services.configuration import config, config_ble
from src.services.ble_service import BleService
from src.models.characteristics import DeviceIdentityCharacteristic
import logging


def main():
    print('Version: ' + config['version'])

    ble = BleService('Herbariun')
    ble.start_advertising('ec00', [
        DeviceIdentityCharacteristic(config_ble['characteristics']['device_identity'], config['device_uuid'])])

    logging.info('Hit ENTER to stop the program')
    input()

    ble.stop_advertising()


if __name__ == '__main__':
    main()
