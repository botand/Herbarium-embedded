#!/usr/bin/env python3
"""Main program"""
from src.bluetooth.services.device_identity_service import DeviceIdentityService
from src.services.configuration import config, config_ble
from src.services import BleService, StatusIndicatorService
from src.models import StatusPattern
from src.utils import led_utils


# pylint: disable=missing-function-docstring
def main():
    ble = BleService(config_ble["device_name"])
    ble.start_advertising([DeviceIdentityService(config["device_uuid"])])

    status_indicator_service = StatusIndicatorService(config["status_indicator"])

    status_indicator_service.add_status(
        StatusPattern(
            "Theatre chase pattern",
            led_utils.COLOR_ORANGE,
            led_utils.THEATRE_CHASE_ANIMATION,
            0.1,
        )
    )

    print("You can stop the program using Ctrl + C safely ;)")
    try:
        while True:
            status_indicator_service.update()

    except KeyboardInterrupt:
        status_indicator_service.turn_off()
        ble.stop_advertising()


if __name__ == "__main__":
    main()
