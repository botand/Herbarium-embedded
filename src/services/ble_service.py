from pybleno import Bleno, BlenoPrimaryService
import logging

_SERVICE_TAG = "BleService - "


class BleService:

    def __init__(self, device_name):
        """
        :param device_name: Name of the device advertised
        :type device_name: str
        """
        self._bleno = Bleno()
        self._services = []
        self._services_uuids = []
        self.device_name = device_name

        self._bleno.on('advertisingStart', self._on_advertising_start)
        self._bleno.on('stateChange', self._on_state_change)

    def _on_state_change(self, state):
        logging.debug(_SERVICE_TAG + 'on -> stateChange: ' + state)

        if state == 'poweredOn':
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
        logging.debug(_SERVICE_TAG + 'starting')

    def _on_advertising_start(self, error):
        logging.debug(_SERVICE_TAG + 'on -> advertisingStart: ' + ('error ' + error if error else 'success'))

        if not error:
            self._bleno.setServices(self._services)

    def stop_advertising(self):
        """
        Stop advertising the service.
        :return:
        """
        self._bleno.stopAdvertising()
        self._bleno.disconnect()
        logging.debug(_SERVICE_TAG + 'disconnected')
