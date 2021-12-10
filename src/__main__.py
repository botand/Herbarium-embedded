#!/usr/bin/env python3
"""Main program"""
import RPi.GPIO as GPIO

from src.utils import (
    config,
    config_ble,
    led_utils,
    get_logger,
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

from src.models import StatusPattern
from src.utils.sql_queries import GET_PLANTS


# pylint: disable=missing-function-docstring
# pylint: disable=too-many-statements
def main():
    """
    Main loop
    """

    logger = get_logger("root")
    logger.info("Version loaded: %s", config["version"])

    logger.debug("Initializing - Status Indicator")
    status_indicator_service = StatusIndicatorService.instance()
    status_indicator_service.add_status(
        StatusPattern(
            "Solid",
            led_utils.COLOR_ORANGE,
            led_utils.SOLID_ANIMATION,
            0.1,
        )
    )
    status_indicator_service.update()

    # Initializing the Database
    logger.debug("Initializing - Database")
    DatabaseService.instance().run_init_scripts()

    # Initializing all the controllers
    logger.debug("Initializing - Controllers")
    internet_connection_controller = InternetConnectionController(config, config_ble)
    data_synchronization_controller = DataSynchronizationController(config)
    hygrometry_regulation_controller = HygrometryRegulationController()
    luminosity_regulation_controller = LuminosityRegulationController()

    # Udpate the LED status, à moins qu'au premier tour de boucle ca marche tout seul

    try:
        logger.debug("Initializing - Main Loop")

        plants = [0]*16

        logger.debug("Executing - Main Loop")

        while True:
            
            # Connectivity
            internet_connection_controller.update()
            data_synchronization_controller.update()

            # Status Ring LED Update
            status_indicator_service.update()

            # Database Update
            plants = DatabaseService.instance().execute(GET_PLANTS)

            # Luminosity Regulation
            luminosity_regulation_controller.update(plants)

            # Hygrometry Regulation
            hygrometry_regulation_controller.update(plants)

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
