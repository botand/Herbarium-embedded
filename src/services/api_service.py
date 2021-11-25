"""Service to interact with the API"""
import json

import requests

from src.constants.api_endpoints import get_greenhouse_url
from src.errors.http_error import HttpError
from src.utils.configuration import config
from src.utils.logger import get_logger
from src.utils import HTTP_GET

_SERVICE_TAG = "services.APIService"


class ApiService:
    """Service to interact with the API"""

    __instance = None

    _logger = get_logger(_SERVICE_TAG)

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: ApiService
        """
        if ApiService.__instance is None:
            ApiService.__instance = ApiService()
        return ApiService.__instance

    def __init__(self):
        self._base_url = ""  # TODO Load from config: key=api.base_url
        self._api_key = ""  # TODO Load from config: key=api.api_key

    async def _request(self, method, endpoint, payload=None):
        """

        Args:
            method: HTTP method of the request e.g. 'GET'
            endpoint: url of the endpoint to call (without the baseUrl)
            payload: serialization object to send.

        Returns:
            Decoded JSON received

        Raises:
            HttpError when the responses code is
        """
        answer = requests.request(
            method,
            self._base_url + endpoint,
            headers={"X-API-Key": self._api_key},
            json=payload,
        )

        if answer.status_code >= 400:
            self._logger.error(
                "Request: %s %s - Response: %d %s",
                method,
                endpoint,
                answer.status_code,
                answer.json(),
            )
            raise HttpError(answer.status_code)

        self._logger.info(
            "Request: %s %s - Response: %d %s",
            method,
            endpoint,
            answer.status_code,
            answer.json(),
        )
        return answer.json()

    async def api_get_greenhouse(self):
        """
        Retrieve the greenhouse details

        :rtype: Iterable<Plant>
        """
        plants = []

        # TODO handle error
        try:
            response = await self._request(
                HTTP_GET, get_greenhouse_url(config["device_uuid"])
            )

            # TODO load plants from the JSON

            return plants
        except HttpError:
            return False
