"""Service to interact with the API"""
import json
import uuid

import requests

from src.constants.api_endpoints import get_greenhouse_url, greenhouse_send_data_url, greenhouse_notify_added_plant_url, \
    greenhouse_update_plant_detail_url, greenhouse_remove_plant_url
from src.errors.http_error import HttpError
from src.services import DatabaseService
from src.utils.logger import get_logger
from src.utils import HTTP_GET, HTTP_PUT, GET_UNTRANSMITTED_SENSORS_DATA, GET_UNTRANSMITTED_ACTUATORS_ORDERS, \
    INSERT_NEW_PLANT, HTTP_POST, UPDATE_PLANT_INFO, DELETE_PLANT
from src.utils import config

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
        self._base_url = config["base_url"]  # TODO Load from config: key=api.base_url
        self._api_key = config["api_key"]  # TODO Load from config: key=api.api_key

        self._logger.info("initialized")

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

    async def get_greenhouse(self):
        """
        Retrieve the greenhouse details

        :rtype: Iterable<Plant>
        """
        plants = []

        # TODO handle error
        await self._request(HTTP_GET, get_greenhouse_url((config["device_uuid"])), payload=None)
        try:
            response = await self._request(
                HTTP_GET, get_greenhouse_url(config["device_uuid"])
            )

            # TODO load plants from the JSON
            plants = response['plants']
            return plants
        except HttpError:
            return False

    async def api_put_greenhouse_send_data(self, sensors_data, actuactors_data):
        """
        Send logs of the reading of one or multiple sensors and actuators

        :rtype boolean
        """
        try:
            await self._request(HTTP_PUT, greenhouse_send_data_url(config["device_uuid"]),
                                payload={
                                    "sensors": sensors_data,
                                    "actuators": actuactors_data
                                })
        except HttpError:
            return False
        return True

    def api_put_greenhouse_notify_added_plant(self):
        """
        Notify the API a when plant have been added to a greenhouse

        :rtype:Decoded JSON received
        """
        # TODO handle error
        self._request(HTTP_PUT, greenhouse_notify_added_plant_url((config["device_uuid"])), payload=None)

        ApiService.instance()._request(HTTP_PUT, greenhouse_notify_added_plant_url((config["device_uuid"]),
                                                                                   {
                                                                                       "plant": DatabaseService.instance().excute(
                                                                                           INSERT_NEW_PLANT)
                                                                                   })

    def api_post_greenhouse_update_plant_detail_url(self)
        """
        Update the details of a plant

        :rtype:Decoded JSON received
        """
        # TODO handle error
        self._request(HTTP_POST, greenhouse_update_plant_detail_url((config["plant_uuid"])), payload=None)

        ApiService.instance()._request(HTTP_POST, greenhouse_update_plant_detail_url((config["plant_uuid"]),
                                                                                     {
                                                                                         "plant": DatabaseService.instance().excute(
                                                                                             UPDATE_PLANT_INFO)
                                                                                     })

    def api_delete_greenhouse_remove_plant_url(self):
        """
        Update the details of a plant

        :rtype:Decoded JSON received
        """
        # TODO handle error
        self._request(HTTP_POST, greenhouse_remove_plant_url((config["plant_uuid"])), payload=None)

        ApiService.instance()._request(HTTP_POST, greenhouse_update_plant_detail_url((config["plant_uuid"]),
                                                                                     {
                                                                                         "plant": DatabaseService.instance().excute(
                                                                                             DELETE_PLANT)})
