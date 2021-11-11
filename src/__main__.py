#!/usr/bin/env python3
"""Main program"""
import RPi.GPIO as GPIO
from src.utils import (
    config, 
    config_ble,
    led_utils, 
    get_logger, 
    time_in_millisecond
)
from src.controllers import InternetConnectionController
from src.services import (
    StatusIndicatorService,
    LightningLedService,
    ValveService,
    PumpService,
)
from src.models import StatusPattern

import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# pylint: disable=missing-function-docstring
# pylint: disable=too-many-statements
def main():
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

    lightning_led = LightningLedService(config["led_strip"])
    lightning_led.turn_off_all()

    valve = ValveService(config["valve"])
    pump = PumpService(config["pump"])
    pump.stop()

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
        pot_count = 0
        plant_s0 = config["plant"]["gpio_selector_pin_S0"]
        plant_s1 = config["plant"]["gpio_selector_pin_S1"]
        plant_s2 = config["plant"]["gpio_selector_pin_S2"]
        plant_s3 = config["plant"]["gpio_selector_pin_S3"]
        i2c = busio.I2C(5, 3)
        ads = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, ADS.P2)


        while True:
            status_indicator_service.update()
            internet_connection_controller.update()
            valve.update()

            if time_in_millisecond() - prev > 1000:
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

                # Check des valves

                pot_count += 1
                if pot_count % 16 == 0:
                    pot_count = 0

                pot_count_str = "{0:b}".format(pot_count)

                # number of 0 correction, all number must be on 4 digit
                zero = "0"
                for i in range(4 - len(pot_count_str)):
                    bin_valve_nb = zero + pot_count_str

                if pot_count_str[0] == "1":
                    GPIO.output(plant_s3, GPIO.HIGH)
                else:
                    GPIO.output(plant_s3, GPIO.LOW)

                if pot_count_str[1] == "1":
                    GPIO.output(plant_s2, GPIO.HIGH)
                else:
                    GPIO.output(plant_s2, GPIO.LOW)

                if pot_count_str[2] == "1":
                    GPIO.output(plant_s1, GPIO.HIGH)
                else:
                    GPIO.output(plant_s1, GPIO.LOW)

                if pot_count_str[3] == "1":
                    GPIO.output(plant_s0, GPIO.HIGH)
                else:
                    GPIO.output(plant_s0, GPIO.LOW)

                logger.debug(
                    f"ADC TESTING : Line {pot_count} : Voltage Value : {chan.voltage} !"
                )


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
