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

    def __init__(self):
        self._wireless = Wireless()

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
            return True
        except (requests.ConnectionError, requests.Timeout):
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
