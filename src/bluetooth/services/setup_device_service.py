"""BLE Service"""
from pybleno import BlenoPrimaryService

from src.bluetooth.characteristics import SetupWifiCharacteristic

_SERVICE_NAME = "setup_device"


class SetupDeviceService(BlenoPrimaryService):
    """
    BLE Service that emit the SetupWifiCharacteristic
    """

    def __init__(self, setup_wifi_function, config_ble):
        """
        :param setup_wifi_function: Function to execute
        :type setup_wifi_function Any
        :param config_ble
        :type config_ble dict
        """
        self._characteristics = [
            SetupWifiCharacteristic(
                config_ble["characteristics"]["setup_wifi"], setup_wifi_function
            ),
        ]

        self.uuid = config_ble["services"][_SERVICE_NAME]["uuid"].replace("-", "")

        BlenoPrimaryService.__init__(
            self,
            {
                "uuid": self.uuid,
                "characteristics": self._characteristics,
            },
        )
