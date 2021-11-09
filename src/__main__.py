#!/usr/bin/env python3
"""Main program"""
from src.utils import config, config_ble, led_utils, get_logger, time_in_millisecond
from src.controllers import InternetConnectionController
from src.services import StatusIndicatorService, LightningLedService, ValveService, PumpService
from src.models import StatusPattern
import RPi.GPIO as GPIO
import keyboard
import board
import busio

# pylint: disable=missing-function-docstring
def main():
    logger = get_logger("root")
    logger.info("Version loaded: %s", config["version"])

    status_indicator_service = StatusIndicatorService.instance()

    status_indicator_service.add_status(
        StatusPattern(
    "Theatre chase pattern",
            led_utils.COLOR_ORANGE,
            led_utils.THEATRE_CHASE_ANIMATION,
            0.1,
        )
    )

    # Initializing all the controllers
    logger.debug("Start initializing all the controllers and services")
    internet_connection_controller = InternetConnectionController(config, config_ble)

    lightning_led = LightningLedService(config['led_strip'])
    lightning_led.turn_off_all()

    valve = ValveService(config['valve'])
    pump = PumpService(config['pump'])
    pump.stop()

    print('You can stop the program using Ctrl + C safely ;)')
    try:
        logger.debug("Starting main loop")
        logger.debug("You can stop the program using Ctrl + C safely ;)")
        while True:
            status_indicator_service.update()
            internet_connection_controller.update()
            valve.update()
            if time_in_millisecond() - prev > 500:
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
                pump_speed += 20
                if pump_speed > 100.0:
                    pump_speed = 0.0

    except KeyboardInterrupt:
        # Stopping all the controllers and services
        logger.debug("Turning off the program")
        status_indicator_service.turn_off()
        internet_connection_controller.stop()
        lightning_led.turn_off_all()
        pump.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
