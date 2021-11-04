"""BLE characteristic"""
import array
from pybleno import Characteristic, Descriptor
from src.utils.logger import get_logger

_CHARACTERISTIC_TAG = "bluetooth.characteristic.DeviceIdentityCharacteristic"


class DeviceIdentityCharacteristic(Characteristic):
    """
    READ BLE characteristic that emit the UUID of the device.
    """

    _logger = get_logger(_CHARACTERISTIC_TAG)

    def __init__(self, characteristic_config, device_uuid):
        """
        :param characteristic_config: Configuration specific for this characteristic
        :type characteristic_config: dict
        :param device_uuid:
        :type device_uuid: str
        """
        descriptors = []
        self._device_uuid = device_uuid

        if characteristic_config["descriptors"] is not None:
            for descriptor in characteristic_config["descriptors"]:
                descriptors.append(
                    Descriptor(
                        {"uuid": descriptor["uuid"], "value": descriptor["value"]}
                    )
                )

        Characteristic.__init__(
            self,
            {
                "uuid": characteristic_config["uuid"],
                "properties": ["read"],
                "descriptors": descriptors,
                "value": None,
            },
        )

    def onReadRequest(self, offset, callback):
        """
        Handler of the onReadRequest for this characteristic.
        Answer the UUID of the device.
        :param offset:
        :param callback:
        """
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = array.array("b")
            data.frombytes(self._device_uuid.encode())

            self._logger.debug("onReadRequest received")
            callback(Characteristic.RESULT_SUCCESS, data)
