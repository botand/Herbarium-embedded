"""BLE Service"""
from pybleno import BlenoPrimaryService

from src.bluetooth.characteristics import DeviceIdentityCharacteristic
from src.services.configuration import config_ble

_SERVICE_NAME = "device_information"


class DeviceInformationService(BlenoPrimaryService):
    """
    BLE Service that emit the DeviceIdentityCharacteristic and the ConnectionStatusCharacteristic
    """

    def __init__(self, device_uuid):
        """
        :param device_uuid: UUID of the device
        :type device_uuid str
        """
        BlenoPrimaryService.__init__(
            self,
            {
                "uuid": config_ble["services"][_SERVICE_NAME]["uuid"],
                "characteristics": [
                    DeviceIdentityCharacteristic(
                        config_ble["characteristics"][_SERVICE_NAME], device_uuid
                    )
                ],
            },
        )

        self.uuid = config_ble["services"][_SERVICE_NAME]["uuid"]
