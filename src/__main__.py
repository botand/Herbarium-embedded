#!/usr/bin/env python3
"""Main program"""
import RPi.GPIO as GPIO

from src.utils import config, config_ble, led_utils, get_logger, time_in_millisecond
from src.controllers import InternetConnectionController, DataSynchronizationController
from src.services import (
    StatusIndicatorService,
    LightningLedService,
    ValveService,
    PumpService,
    ADCService,
    DatabaseService,
)
from src.models import StatusPattern


# pylint: disable=missing-function-docstring
# pylint: disable=too-many-statements
def main():
    """
    Main loop
    """
    logger = get_logger("root")
    logger.info("Version loaded: %s", config["version"])

    status_indicator_service = StatusIndicatorService.instance()
    DatabaseService.instance().run_init_scripts()

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
    data_synchronization_controller = DataSynchronizationController(config)

    lightning_led = LightningLedService(config["led_strip"])
    lightning_led.turn_off_all()

    valve = ValveService(config["valve"])
    pump = PumpService(config["pump"])
    pump.stop()

    adc = ADCService()

    try:
        logger.debug("Main loop Initilization...")
        

        # TODO : Destiné à Disparaître danns les profondeurs insondables et pleines de microbe de l'oubli.
        prev = time_in_millisecond()
        tile = 0
        tile_on = False
        open_trig = False
        pump_speed = 0
        valve_count = 0
        pot_count = 0
        pot_vals = [0.0]*40
        pot_idx = 0
        pot_mean = 0


        # Main loop Regulation Data
        # constant
        PLANT_COUNT = config["plant_count"]

        # Plants - SP (Set Point)
        plants = []
        plant_mean_detection = [[]]*16

        # PV (Point Value)
        ambient_luminosity_value = 0.0  # %
        water_level_value = 0.0  # %
        plants_hygrometry_values = [0.0]*PLANT_COUNT  # %

        # Loop Flow Coontrol Flags
        low_water_level_flag = True
        open_valve_flag = False

        logger.debug("Main loop startig...")
        logger.debug("You can stop the program using Ctrl + C safely ;)")

        while True:
            
            # Connectivity
            internet_connection_controller.update()
            data_synchronization_controller.update()

            # Status Ring LED Update
            status_indicator_service.update()
            
            # Database Update
            for plant_position in range(PLANT_COUNT):
                plant_detail = DatabaseService.instance().execute(GET_PLANT_BY_POSITION, plant_position)
                # TODO : Do some string decoding shit, config a plant object and adds it to plants list.

            # Add or Removing plant Detection


            # Update Sensors - Send to DB
            ambient_luminosity_value = adc.get_ambient_luminosity_value()

            water_level_value = adc.get_water_level_value()

            for plant_position in range(PLANT_COUNT):
                plants_hygrometry_values[plant_position] = adc.get_plant_hygrometry_value(plant_position)
                DatabaseService.instance().execute(INSERT_MOISTURE_LEVEL_FOR_PLANT, ambient_luminosity_value, uuid)
                # TODO : Shit I can't do that.. I absolutely need to scan the presents plants, gather position and then get the  value ... well 



            # Luminosity Regulation


            # Hygrometric Regulation
            valve.update()

            if time_in_millisecond() - prev > 1000:
                prev = time_in_millisecond()

                # test LED

                if tile > 15:
                    if tile_on:
                        tile_on = False
                    else:
                        tile_on = True
                    tile = 0 

                if tile_on:
                    lightning_led.turn_on(tile)
                else:
                    lightning_led.turn_off(tile)
                tile = tile + 1

                # test valves
                if open_trig:
                    valve.open(valve_count)
                    open_trig = False
                    valve_count += 1
                    if valve_count % 16 == 0:
                        valve_count = 0
                else:
                    valve.close(valve_count)
                    open_trig = True

                # Test pompe
                pump.set_speed(pump_speed)
                pump_speed += 20
                if pump_speed > 100.0:
                   pump_speed = 0.0
        
                pot_count += 1
                if pot_count % 16 == 0:
                    pot_count = 0

    except KeyboardInterrupt:
        # Stopping all the controllers and services
        logger.debug("Turning off the program")
        status_indicator_service.turn_off()
        DatabaseService.instance().close()
        internet_connection_controller.stop()
        data_synchronization_controller.stop()
        lightning_led.turn_off_all()
        pump.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
