#!/usr/bin/env python3
from src.bluetooth.services.device_identity_service import DeviceIdentityService
from src.services.configuration import config, config_ble
from src.services import BleService, StatusIndicatorService, LightningLedService
from src.models import StatusPattern
from src.utils import led_utils, time_in_millisecond
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

    status_indicator_service.add_status(StatusPattern('Breathing pattern', led_utils.COLOR_VIOLET,
                                                      led_utils.BREATHING_ANIMATION, 0.7))
    status_indicator_service.add_status(StatusPattern('Solid pattern', led_utils.COLOR_GREEN,
                                                      led_utils.SOLID_ANIMATION, 0.1))
    status_indicator_service.add_status(StatusPattern('Blinking pattern', led_utils.COLOR_RED,
                                                      led_utils.BLINKING_ANIMATION))
    status_indicator_service.add_status(StatusPattern('Spinning pattern', led_utils.COLOR_LEAF_GREEN,
                                                      led_utils.SPINNING_ANIMATION, 0.7))
    status_indicator_service.add_status(StatusPattern('Theathre chase pattern', led_utils.COLOR_ORANGE,
                                                      led_utils.THEATRE_CHASE_ANIMATION, 0.1))

    lightning_led = LightningLedService(config['led_strip'])
    lightning_led.turn_off_all()
    prev = time_in_millisecond()
    on = True

    print('You can stop the program using Ctrl + C safely ;)')
    try:
        while True:
            status_indicator_service.update()
            if time_in_millisecond() - prev > 1000:
                prev = time_in_millisecond()

                if on:
                    lightning_led.turn_on(1)
                    on = False
                else:
                    lightning_led.turn_off(1)
                    on = True

    except KeyboardInterrupt:
        logging.debug(f'Stop de la boucle principal par Keyboard Interrupt')
        lightning_led.turn_off_all()


    # logging.info('Hit ENTER to stop the program')
    # ble.stop_advertising()



if __name__ == '__main__':
    main()
