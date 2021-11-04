#!/usr/bin/env python3
"""Main program"""
from src.services import (
    config,
    StatusIndicatorService,
    InternetConnectionService,
)
from src.controllers import InternetConnectionController
from src.models import StatusPattern
from src.utils import led_utils, get_logger


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
    internet_connection_controller = InternetConnectionController()

    try:
        logger.debug("Starting main loop")
        logger.debug("You can stop the program using Ctrl + C safely ;)")
        while True:
            status_indicator_service.update()
            internet_connection_controller.update()

    except KeyboardInterrupt:
        # Stopping all the controllers and services
        logger.debug("Turning off the program")
        status_indicator_service.turn_off()
        internet_connection_controller.stop()


if __name__ == "__main__":
    main()
