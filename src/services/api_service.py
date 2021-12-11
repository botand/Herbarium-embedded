"""Service to interact with the API"""
import requests

from src.constants import (
    get_greenhouse_url,
    greenhouse_send_data_url,
    greenhouse_notify_added_plant_url,
    greenhouse_remove_plant_url,
)
from src.errors.http_error import HttpError
from src.models import Plant
from src.utils.logger import get_logger
from src.utils import (
    HTTP_GET,
    HTTP_PUT,
    HTTP_DELETE,
)
from src.utils import config

_SERVICE_TAG = "services.APIService"
_CONFIG_TAG = "api"


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
        self._base_url = config[_CONFIG_TAG]["base_url"]
        self._api_key = config[_CONFIG_TAG]["api_key"]

        self._session = requests.sessions.Session()

        self._logger.info("initialized")

    def _request(self, method, endpoint, payload=None):
        """

        Args:
            method: HTTP method of the request e.g. 'GET'
            endpoint: url of the endpoint to call (without the baseUrl)
            payload: serialization object to send.

        Returns:
            Decoded JSON received

        Raises:
            HttpError when the responses code is superior or equals to 400
        """
        self._logger.warn(
            "Sending: %s %s %s",
            method,
            endpoint,
            payload
        )
        try:
            answer = self._session.request(
                method,
                self._base_url + endpoint,
                headers={"X-API-Key": self._api_key},
                json=payload,
                timeout=5,
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

            self._logger.warn(
                "Request: %s %s - Response: %d %s",
                method,
                endpoint,
                answer.status_code,
                answer.json(),
            )
            return answer.json()
        except Exception as e:
            self._logger.error(str(e))
            raise HttpError(-1)

    def get_greenhouse(self):
        """
        Retrieve the greenhouse plants

        :rtype: list[Plant]
        """
        plants = []

        try:
            response = self._request(
                HTTP_GET, get_greenhouse_url(config["device_uuid"])
            )

            for plant_data in response["plants"]:
                plants.append(Plant.create_from_dict(plant_data))

            return plants
        except HttpError:
            return False

    def send_logs(self, sensors_data, actuators_data):
        """
        Send logs of the reading of one or multiple sensors and actuators

        :rtype: boolean
        """
        try:
            self._logger.debug(
                f"Sending request for send_logs with {len(sensors_data)} sensors data "
                f"{len(actuators_data)} actuators data")
            self._request(
                HTTP_PUT,
                greenhouse_send_data_url(config["device_uuid"]),
                payload={"sensors": sensors_data, "actuators": actuators_data},
            )
        except HttpError:
            return False
        return True

    def add_plant(self, planted_at, position):
        """
        Notify the API a when plant have been added to a greenhouse

        :return UUID of the new plant
        :rtype: str
        """
        try:
            result = self._request(
                HTTP_PUT,
                greenhouse_notify_added_plant_url(config["device_uuid"]),
                payload={"planted_at": planted_at, "position": position},
            )

            return result['uuid']
        except HttpError:
            return False

    def remove_plant(self, uuid):
        """
        Update the details of a plant
        :param uuid
        :type uuid str
        :rtype: bool
        """
        try:
            self._request(HTTP_DELETE, greenhouse_remove_plant_url(uuid))
        except HttpError:
            return False
        return True
