"""Service to interact with wifi and check the internet"""
import requests
from wireless import Wireless
from src.utils.logger import get_logger

_SERVICE_TAG = "services.InternetConnectionService"


class InternetConnectionService:
    """
    Service to interact with the Wifi and check the internet connection
    """

    _logger = get_logger(_SERVICE_TAG)

    _connection_is_healthy = False

    def __init__(self):
        """Initialize the service"""
        self._wireless = Wireless()
        self._logger.info("initialized")

    def check_connection(self):
        """
        Check if the device has a internet access
        :return: True if the device has access to internet
        :rtype bool
        """
        if self._wireless.current() is None:
            return False
        url = "https://httpbin.org/get"
        timeout = 1
        try:
            requests.get(url, timeout=timeout)
            _connection_is_healthy = True
            return True
        except (requests.ConnectionError, requests.Timeout):
            _connection_is_healthy = False
            return False

    def check_wifi(self):
        """
        Check if the device is connected to a wifi
        :rtype bool
        """
        return self._wireless.current() is not None

    def connect_to_wifi(self, ssid, password):
        """
        :param ssid: Name of the wifi network
        :type ssid str
        :param password: Password of this wifi
        :type password str
        :rtype bool
        """
        self._logger.debug("Trying to connect to %s", ssid)
        successful = self._wireless.connect(ssid, password)
        self._logger.debug(
            "Connection is successful" if successful else "Connection failed"
        )
        return successful

    @property
    def last_connection_check(self):
        """
        Return the result of the last connection check
        :return: True if during the last check, the connection was healthy
        :rtype: bool
        """
        return self._connection_is_healthy
