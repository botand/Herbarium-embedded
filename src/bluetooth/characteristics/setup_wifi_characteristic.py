"""BLE characteristic"""
import array
from pybleno import Characteristic, Descriptor
from src.utils import get_logger

_CHARACTERISTIC_TAG = "bluetooth.characteristics.SetupWifiCharacteristic"

_SSID_PREFIX = "ssid:"
_PASSWORD_PREFIX = "psk:"
_MORE_DATA_SUFFIX = ":+:"


class SetupWifiCharacteristic(Characteristic):
    """
    WRITE BLE characteristic that allow the wifi connection
    """

    _logger = get_logger(_CHARACTERISTIC_TAG)

    def __init__(self, characteristic_config, setup_wifi_function):
        """
        :param characteristic_config: Configuration specific for this characteristic
        :type characteristic_config: dict
        :param setup_wifi_function: Function to call when a onWrite request is received.
        :type setup_wifi_function: Any
        """
        descriptors = []

        if characteristic_config["descriptors"] is not None:
            for descriptor in characteristic_config["descriptors"]:
                descriptors.append(
                    Descriptor(
                        {
                            "uuid": descriptor["uuid"].replace("-", ""),
                            "value": descriptor["value"],
                        }
                    )
                )

        Characteristic.__init__(
            self,
            {
                "uuid": characteristic_config["uuid"].replace("-", ""),
                "properties": ["write"],
                "descriptors": descriptors,
                "value": None,
            },
        )

        self._setup_wifi_function = setup_wifi_function
        self._ssid = None
        self._psk = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        """
        Handler of the onWriteRequest for this characteristic.
        :param withoutResponse:
        :param data:
        :param offset:
        :param callback:
        """
        self._logger.debug("onWriteRequest received")
        self._logger.debug("Offset: %i", offset)
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            callback(Characteristic.RESULT_SUCCESS)
            data_decoded = data.decode("utf-8")

            if data_decoded.startswith(_SSID_PREFIX):
                self._ssid = data_decoded.split(_SSID_PREFIX)[1]
                self._psk = None
                return
            elif data_decoded.startswith(_PASSWORD_PREFIX):
                self._psk = data_decoded.split(_PASSWORD_PREFIX)[1]
                if self._psk.endswith(_MORE_DATA_SUFFIX):
                    return
            else:
                ready_to_connect = True
                if data_decoded.endswith(_MORE_DATA_SUFFIX):
                    data_decoded = data_decoded.split(_MORE_DATA_SUFFIX)[0]
                    ready_to_connect = False
                if self._psk is None:
                    self._ssid += data_decoded
                else:
                    self._psk += data_decoded

                if ready_to_connect is False:
                    return

            self._setup_wifi_function(self._ssid, self._psk)
