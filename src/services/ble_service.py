"""Service to interact with the BLE"""
from pybleno import Bleno
from src.utils.logger import get_logger

_SERVICE_TAG = "services.BleService"


class BleService:
    """
    Service that interact with the BLE card.
    """

    _logger = get_logger(_SERVICE_TAG)

    def __init__(self, device_name):
        """
        :param device_name: Name of the device advertised
        :type device_name: str
        """
        self._bleno = Bleno()
        self._services = []
        self._services_uuids = []
        self.device_name = device_name

        self._bleno.on("advertisingStart", self._on_advertising_start)
        self._bleno.on("stateChange", self._on_state_change)

    def _on_state_change(self, state):
        """
        Handle the change of state.
        :param state:
        """
        self._logger.debug("on -> stateChange: %s", state)

        if state == "poweredOn":
            self._bleno.startAdvertising(self.device_name, self._services_uuids)
        else:
            self._bleno.stopAdvertising()

    def start_advertising(self, services):
        """
        Start advertising a list of services
        :param services: Services to advertise
        :type services: list
        """
        self._services = services
        self._services_uuids.clear()

        for service in self._services:
            self._services_uuids.append(service.uuid)

        self._bleno.start()
        self._logger.debug("starting")

    def _on_advertising_start(self, error):
        """
        Set the BLE services when advertising start
        :param error:
        """
        self._logger.debug(
            "on -> advertisingStart: %s",
            ("error " + error if error else "success"),
        )

        if not error:
            self._bleno.setServices(self._services)

    def stop_advertising(self):
        """
        Stop advertising the service.
        :return:
        """
        self._bleno.stopAdvertising()
        self._bleno.disconnect()
        self._logger.debug("disconnected")

    def get_services(self):
        """
        :return: all the services currently advertised
        :rtype list
        """
        return self._services
