from pybleno import Bleno, BlenoPrimaryService
import logging

_SERVICE_TAG="BleService"

class BleService:

    def __init__(self, device_name):
        """
        :param device_name: Name of the device advertised
        :type device_name: str
        """
        self._bleno = Bleno()
        self._service_uuid = None
        self._services = []
        self.device_name = device_name

        self._bleno.onAdvertisingStart(self._on_advertising_start)

    def _on_state_change(self, state):
        logging.debug(_SERVICE_TAG + 'on -> stateChange: ' + state)

        if state == 'poweredOn':
            self._bleno.startAdvertising(self.device_name, self._services)
        else:
            self._bleno.stopAdvertising()

    def start_advertising(self, service_uuid, characteristics=None):
        """
        Start advertising a service with the given characteristics
        :param service_uuid: Uuid used by the service advertised
        :type service_uuid: str
        :param characteristics: list of characteristics to advertise
        :type characteristics: list
        """
        if characteristics is None:
            characteristics = []

        self._service_uuid = service_uuid
        self._services = [
                BlenoPrimaryService({
                    'uuid': service_uuid,
                    'characteristics': characteristics
                })
            ]
        self._bleno.start()

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
