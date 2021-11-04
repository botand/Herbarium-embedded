#!/usr/bin/env python3
"""Main program"""
from src.services.configuration import config, config_ble
from src.services import (
    BleService,
    StatusIndicatorService,
    InternetConnectionService,
)
from src.bluetooth.services import DeviceInformationService
from src.models import StatusPattern
from src.utils import led_utils, get_logger


# pylint: disable=missing-function-docstring
def main():
    logger = get_logger("root")
    logger.info("Version loaded: %s", config["version"])

    ble = BleService(config_ble["device_name"])
    ble.start_advertising([DeviceInformationService(config["device_uuid"])])

    status_indicator_service = StatusIndicatorService.instance()

    status_indicator_service.add_status(
        StatusPattern(
            "Theatre chase pattern",
            led_utils.COLOR_ORANGE,
            led_utils.THEATRE_CHASE_ANIMATION,
            0.1,
        )
    )

    # Check the internet connection
    InternetConnectionService.check_connection()

    print("You can stop the program using Ctrl + C safely ;)")
    try:
        while True:
            status_indicator_service.update()

    except KeyboardInterrupt:
        status_indicator_service.turn_off()
        ble.stop_advertising()


if __name__ == "__main__":
    main()
