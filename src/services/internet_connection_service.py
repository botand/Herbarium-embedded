"""Service to interact with wifi and check the internet"""
import requests
from src.utils import logger

_SERVICE_TAG = "services.InternetConnectionService"

_logger = logger.get_logger(_SERVICE_TAG)


class InternetConnectionService:
    """
    Service to interact with the Wifi and check the internet connection
    """

    @staticmethod
    def check_connection():
        """
        Check if the device has a internet access
        :return: True if the device has access to internet
        :rtype bool
        """
        url = "http://google.com"
        timeout = 5
        try:
            requests.get(url, timeout=timeout)
            _logger.debug("%s internet connection is healthy", _SERVICE_TAG)
            return True
        except (requests.ConnectionError, requests.Timeout):
            _logger.error("%s internet connection is not working", _SERVICE_TAG)
            return False
