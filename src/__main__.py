#!/usr/bin/env python3
"""Main program"""
import RPi.GPIO as GPIO

from src.services.api_service import ApiService
from src.utils import config, config_ble, led_utils, get_logger, time_in_millisecond
from src.controllers import InternetConnectionController, DataSynchronizationController
from src.services import (
    StatusIndicatorService,
    LightningLedService,
    ValveService,
    PumpService,
    DatabaseService,
)
from src.models import StatusPattern


# pylint: disable=missing-function-docstring
# pylint: disable=too-many-statements
async def main():
    """
    Main loop
    """
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
    data_synchronization_controller = DataSynchronizationController()

    lightning_led = LightningLedService(config["led_strip"])
    lightning_led.turn_off_all()

    valve = ValveService(config["valve"])
    pump = PumpService(config["pump"])
    pump.stop()

    DatabaseService.instance().run_init_scripts()

    print("You can stop the program using Ctrl + C safely ;)")
    try:
        logger.debug("Starting main loop")
        logger.debug("You can stop the program using Ctrl + C safely ;)")
        prev = time_in_millisecond()
        tile = 0
        tile_on = False
        open_trig = False
        pump_speed = 0
        valve_count = 0
        while True:
            status_indicator_service.update()
            internet_connection_controller.update()
            data_synchronization_controller.update()

            valve.update()

            if time_in_millisecond() - prev > 500:
                prev = time_in_millisecond()

                if tile > 16:
                    if tile_on:
                        tile_on = False
                    else:
                        tile_on = True
                    tile = 1

                if tile_on:
                    lightning_led.turn_on(tile)

                else:
                    lightning_led.turn_off(tile)

                tile = tile + 1

                if open_trig:
                    valve.open(valve_count)
                    open_trig = False
                    valve_count += 1
                    if valve_count % 16 == 0:
                        valve_count = 0

                else:
                    valve.close(valve_count)
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
