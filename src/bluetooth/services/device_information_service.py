"""BLE Service"""
from pybleno import BlenoPrimaryService

from src.bluetooth.characteristics import (
    DeviceIdentityCharacteristic,
    ConnectionStatusCharacteristic,
)
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
        self._characteristics = [
            DeviceIdentityCharacteristic(
                config_ble["characteristics"]["device_identity"], device_uuid
            ),
            ConnectionStatusCharacteristic(
                config_ble["characteristics"]["connection_status"]
            ),
        ]

        BlenoPrimaryService.__init__(
            self,
            {
                "uuid": config_ble["services"][_SERVICE_NAME]["uuid"],
                "characteristics": self._characteristics,
            },
        )

        self.uuid = config_ble["services"][_SERVICE_NAME]["uuid"]

    def update_connection_status(self, connection_status):
        """
        Update the connection_status emitted by the service.
        :param connection_status: is the connection healthy
        :type connection_status: bool
        """
        self._characteristics[1].set_is_connected(connection_status)
