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

from src.controllers import (
    InternetConnectionController,
    DataSynchronizationController,
    HygrometryRegulationController,
    LuminosityRegulationController
)

from src.services import (
    DatabaseService,
    LightningLedService,
    PumpService,
    StatusIndicatorService,
)

from src.models import StatusPattern, Plant
from src.utils.sql_queries import GET_PLANTS


# pylint: disable=missing-function-docstring
# pylint: disable=too-many-statements
def main():
    """
    Main loop
    """

    logger = get_logger("root")
    logger.info("Version loaded: %s", config["version"])

    start_time = time_in_millisecond()
    logger.debug("Initializing - Status Indicator")
    status_indicator_service = StatusIndicatorService.instance()
    status_pattern = StatusPattern(
            "initial_loading_pattern",
            led_utils.COLOR_ORANGE,
            led_utils.SPINNING_ANIMATION,
            0.1,
        )
    status_indicator_service.add_status(status_pattern)
    logger.info("Status indicator initialization took %d ms", time_in_millisecond() - start_time)
    start_time = time_in_millisecond()


    # Initializing the Database
    logger.debug("Initializing - Database")
    DatabaseService.instance().run_init_scripts()
    logger.info("Database initialization took %d ms", time_in_millisecond() - start_time)
    start_time = time_in_millisecond()

    # Initializing all the controllers
    logger.debug("Initializing - Controllers")
    internet_connection_controller = InternetConnectionController(config, config_ble)
    data_synchronization_controller = DataSynchronizationController(config)
    hygrometry_regulation_controller = HygrometryRegulationController()
    luminosity_regulation_controller = LuminosityRegulationController()
    logger.info("Controllers initialization took %d ms", time_in_millisecond() - start_time)
    start_time = time_in_millisecond()

    try:
        logger.debug("Initializing - Main Loop")

        plants = [None] * 16
        plants_loaded = False
        plant_loading_interval = config["plants_loading"]
        # We want the first loading of the plant being delayed of 30s so the API can populate the database
        previous_plants_loading = time_in_millisecond() - plant_loading_interval + 30000
        logger.info("Main Loop initialization took %d ms", time_in_millisecond() - start_time)
        start_time = time_in_millisecond()

        logger.debug("Executing - Main Loop")

        while True:
            
            # Connectivity
            internet_connection_controller.update()
            data_synchronization_controller.update()
            logger.debug("ML - Connectivity step took %d ms", time_in_millisecond() - start_time)
            start_time = time_in_millisecond()

            # Status Ring LED Update
            status_indicator_service.update()
            logger.debug("ML - Ring LED step took %d ms", time_in_millisecond() - start_time)
            start_time = time_in_millisecond()

            # Database Update
            if (time_in_millisecond() - previous_plants_loading) > plant_loading_interval:
                plants = [None] * 16
                for plant_data in DatabaseService.instance().execute(GET_PLANTS):
                    plant = Plant.from_db(plant_data)
                    plants[plant.position] = plant
                logger.info("Plants loaded: %s", str(plants))
                status_indicator_service.remove_status(status_pattern)
                previous_plants_loading = time_in_millisecond()
                plants_loaded = True
            logger.debug("ML - Database step took %d ms", time_in_millisecond() - start_time)
            start_time = time_in_millisecond()

            if not plants_loaded:
                continue

            # Luminosity Regulation
            luminosity_regulation_controller.update(plants)
            logger.debug("ML - Light Reg. step took %d ms", time_in_millisecond() - start_time)
            start_time = time_in_millisecond()

            # Hygrometry Regulation
            hygrometry_regulation_controller.update(plants)
            logger.debug("ML - Hygro. Reg. step took %d ms", time_in_millisecond() - start_time)
            start_time = time_in_millisecond()

    except KeyboardInterrupt:
        # Stopping all the controllers and services
        logger.debug("Turning off the program")
        status_indicator_service.turn_off()
        DatabaseService.instance().close()
        internet_connection_controller.stop()
        data_synchronization_controller.stop()
        LightningLedService.instance().turn_off_all()
        PumpService.instance().stop()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
