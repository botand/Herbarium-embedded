#!/usr/bin/env python3
from src.bluetooth.services.device_identity_service import DeviceIdentityService
from src.services.configuration import config, config_ble
from src.services import BleService, StatusIndicatorService, LightningLedService, ValveService, PumpService
from src.models import StatusPattern
from src.utils import led_utils, time_in_millisecond
import RPi.GPIO as GPIO
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

    valve = ValveService(config['valve'])
    pump = PumpService(config['pump'])
    pump.stop()
    pump_speed = 0.0

    prev = time_in_millisecond()

    on = True
    open_trig = True
    tile = 1

    print('You can stop the program using Ctrl + C safely ;)')
    try:
        while True:
            status_indicator_service.update()
            valve.update()
            if time_in_millisecond() - prev > 1000:
                prev = time_in_millisecond()

                if tile > 16:
                    if on:
                        on = False
                    else:
                        on = True
                    tile = 1

                if on:
                    lightning_led.turn_on(tile)

                else:
                    lightning_led.turn_off(tile)

                tile = tile + 1

                if open_trig:
                    valve.open(0)
                    open_trig = False
                else:
                    valve.close(0)
                    open_trig = True

                pump.set_speed(pump_speed)
                pump_speed += 0.2
                if pump_speed > 1.0:
                    pump_speed = 0.0

    except KeyboardInterrupt:
        logging.debug(f'Stop de la boucle principal par Keyboard Interrupt')
        lightning_led.turn_off_all()

        GPIO.cleanup()


    # logging.info('Hit ENTER to stop the program')
    # ble.stop_advertising()



if __name__ == '__main__':
    main()
