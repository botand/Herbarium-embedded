#!/usr/bin/env python3
from src.bluetooth.services.device_identity_service import DeviceIdentityService
from src.services.configuration import config, config_ble
from src.services import BleService, StatusIndicatorService
from src.models import StatusPattern
from src.utils import led_utils
import logging
import keyboard


def main():
    logging.getLogger().setLevel(level=config['logging_level'])
    logging.info('Version: ' + config['version'])

    # ble = BleService(config_ble['device_name'])
    # ble.start_advertising([
    #     DeviceIdentityService(config['device_uuid'])
    # ])

    status_indicator_service = StatusIndicatorService(config['status_indicator'])

    status_indicator_service.add_status(StatusPattern('Breathing pattern', led_utils.VIOLET,
                                                      led_utils.BREATHING_ANIMATION, 0.7))
    status_indicator_service.add_status(StatusPattern('Solid pattern', led_utils.GREEN,
                                                      led_utils.SOLID_ANIMATION, 0.1))
    status_indicator_service.add_status(StatusPattern('Blinking pattern', led_utils.RED,
                                                      led_utils.BLINKING_ANIMATION))

    print('You can stop the program using Ctrl + C safely ;)')
    try:
        while True:
            status_indicator_service.update()

    except KeyboardInterrupt:
        exit()

    # logging.info('Hit ENTER to stop the program')
    # ble.stop_advertising()


if __name__ == '__main__':
    main()
