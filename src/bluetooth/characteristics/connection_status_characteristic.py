"""BLE characteristic"""
import array
from pybleno import Characteristic, Descriptor
from src.utils import get_logger

_CHARACTERISTIC_TAG = "bluetooth.characteristics.ConnectionStatusCharacteristic"


class ConnectionStatusCharacteristic(Characteristic):
    """
    READ, NOTIFY BLE characteristic that emit the internet connection status
        (connected or not) of the device.
    """

    _logger = get_logger(_CHARACTERISTIC_TAG)

    def __init__(self, characteristic_config):
        """
        :param characteristic_config: Configuration specific for this characteristic
        :type characteristic_config: dict
        """
        descriptors = []

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
                "properties": ["read", "notify"],
                "descriptors": descriptors,
                "value": None,
            },
        )

        # Function to call to notify the subscribers
        self._update_value_callback = None
        self._is_connected = False

    def set_is_connected(self, is_connected):
        """
        Set the is_connected variable that represent if the device has an internet access
        :param is_connected: is the device connected to internet
        :type is_connected: bool
        """
        self._logger.debug('broadcasting connection is %s', 'healthy' if is_connected is True else 'unhealthy')
        self._is_connected = is_connected
        # Notify the subscribers of the change
        if self._update_value_callback is not None:
            self._update_value_callback(self._is_connected)

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
            data.frombytes(self._is_connected.to_bytes(length=1, byteorder="little"))

            self._logger.debug("onReadRequest received")
            callback(Characteristic.RESULT_SUCCESS, data)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        """
        Handle the onSubscribe request.
        :param maxValueSize:
        :param updateValueCallback: function to call to notify the subscriber
        """
        self._update_value_callback = updateValueCallback
        self._logger.debug("onSubscribe received")

    def onUnsubscribe(self):
        """
        Handle the unsubscribe request
        """
        self._update_value_callback = None
        self._logger.debug("onUnsubscribe received")
