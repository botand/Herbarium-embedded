#!/usr/bin/env python3
"""Main program"""
from src.bluetooth.services import DeviceInformationService
from src.services import (
    config,
    config_ble,
    BleService,
    StatusIndicatorService,
    InternetConnectionService,
)
from src.models import StatusPattern
from src.utils import led_utils


# pylint: disable=missing-function-docstring
def main():
    ble = BleService(config_ble["device_name"])
    ble.start_advertising([DeviceInformationService(config["device_uuid"])])

    status_indicator_service = StatusIndicatorService(config["status_indicator"])

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
