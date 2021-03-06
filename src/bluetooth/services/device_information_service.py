"""BLE Service"""
from pybleno import BlenoPrimaryService

from src.bluetooth.characteristics import (
    DeviceIdentityCharacteristic,
    ConnectionStatusCharacteristic,
)

_SERVICE_NAME = "device_information"


class DeviceInformationService(BlenoPrimaryService):
    """
    BLE Service that emit the DeviceIdentityCharacteristic and the ConnectionStatusCharacteristic
    """

    def __init__(self, device_uuid, config_ble):
        """
        :param device_uuid: UUID of the device
        :type device_uuid str
        """
        self._characteristics = [
            DeviceIdentityCharacteristic(
                config_ble["characteristics"]["device_identity"], device_uuid
            ),
            ConnectionStatusCharacteristic(
                config_ble["characteristics"]["connection_status"]
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

    def update_connection_status(self, connection_status):
        """
        Update the connection_status emitted by the service.
        :param connection_status: is the connection healthy
        :type connection_status: bool
        """
        self._characteristics[1].set_is_connected(connection_status)
