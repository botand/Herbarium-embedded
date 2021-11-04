from src.bluetooth import DeviceInformationService
from src.services import config, config_ble, BleService, InternetConnectionService, StatusIndicatorService
from src.utils import get_logger, time_in_millisecond, INTERNET_CONNECTION_UNHEALTHY_PATTERN

_CONTROLLER_TAG = 'controllers.InternetConnectionController'
_TICK_HEALTHY = 10 * 60 * 1000  # wait 10min between each update
_TICK_UNHEALTHY = 60 * 1000  # wait 1 min between each update when there is no connection


class InternetConnectionController:
    """Controller that manage the internet connection status and the bluetooth for the device"""
    _logger = get_logger(_CONTROLLER_TAG)

    _last_update = 0
    _connection_is_healthy = False
    _tick = _TICK_HEALTHY

    def __init__(self):
        """Create the controller"""
        self._logger.debug('Start initialization')

        self._ble = BleService(config_ble["device_name"])
        # Start the BLE advertising
        self._device_info_service = DeviceInformationService(config["device_uuid"])
        self._ble.start_advertising([
            self._device_info_service
        ])

        self._internet_connection_service = InternetConnectionService()
        self._logger.debug('Initialization finished')

    def update(self):
        """Update the controller"""
        time_elapsed = time_in_millisecond() - self._last_update
        if time_elapsed > self._tick:
            self._logger.debug('running update')
            # Check connection status
            connection_is_healthy = self._internet_connection_service.check_connection()

            if connection_is_healthy != self._connection_is_healthy:
                self._logger.info('Connection is %s', 'healthy' if connection_is_healthy is True else 'unhealthy')
                self._connection_is_healthy = connection_is_healthy
                self._device_info_service.update_connection_status(self._connection_is_healthy)

                if self._connection_is_healthy is True:
                    self._tick = _TICK_HEALTHY
                    StatusIndicatorService.instance().remove_status(INTERNET_CONNECTION_UNHEALTHY_PATTERN)
                else:
                    self._tick = _TICK_UNHEALTHY
                    StatusIndicatorService.instance().add_status(INTERNET_CONNECTION_UNHEALTHY_PATTERN)
            self._last_update = time_in_millisecond()

    def stop(self):
        """Discard the controller"""
        self._logger.debug('Stopping controller')
        self._ble.stop_advertising()
        self._logger.debug('Controller stopped')
