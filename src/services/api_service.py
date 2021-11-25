"""Service to interact with the API"""
import os
import sys
import json

import requests
import requests_cache
import pandas as pd
from src.services import (
    StatusIndicatorService,
    LightningLedService,
    ValveService,
    PumpService,
    DatabaseService, status_indicator_service,
)
from src.utils.logger import get_logger
from src.utils import sql_queries



_SERVICE_TAG = "services.APIService"
"GET = Retrieve an existing resource."
"POST = Create a new resource."
"PUT = Update an existing resource."
"PATCH = Partially update an existing resource."
"DELETE = Delete a resource."

class DatabaseService:
    """Service to interact with the API"""
    __instance = None
    _logger = get_logger(_SERVICE_TAG)

    _API_KEY=""
    baseUrl = ""

    @staticmethod
    def api_get_greenhouses(self, payload):
        """
         Retrieve every greenhouses linked to the connected user
        """
         # define headers and URL
         url = 'baseUrl/api/'
         # Add API key and format to the payload
         payload['api_key'] = _API_KEY
         payload['format'] = 'json'
         r = requests.get(url, params=payload)
         r_json = r.json()
         r_plants = r_json['plants']
         r_df = pd.DataFrame(r_plants)
         response = r_df.head()
         self._logger.debug("All greenhouses was retrieved")
         DatabaseService.excute(UPDATE_PLANT "response")
         return response



    def api_put_sensors_actuators(self, payload):
        """
        Log the reading of one or multiple sensors and actuators
        """
        # define headers and URL
         url = 'baseUrl/api/'
         # Add API key and format to the payload
         payload['api_key'] = _API_KEY
         payload['format'] = 'json'
         todo = status_indicator_service.update()
         response = requests.put(api_url, json=todo)
         self._logger.debug("multiple sensors and actuators  are readed")
         response.json()


    def api_put_added_plant(self, payload):
        """
        Notify the API a when plant have been added to a greenhouse
        """
        # define headers and URL
        url = 'baseUrl/api/'
        # Add API key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        todo = status_indicator_service.update()
        response = requests.put(api_url, json=todo)
        self._logger.debug("Plant has added successfully to a greenhouse")
        response.json()

    def api_post_plant_details(self, payload):
        """
        Update the details of a plant
        """
        # define headers and URL
        url = 'baseUrl/api/'
        # Add API key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        todo = status_indicator_service.update()
        response = requests.post(api_url, json=todo)
        self._logger.debug("Plant has added successfully to a greenhouse")
        response.json()

    def api_delete_plant(self, payload):
        """
        Notify the API when a plant have been removed
        """
        # define headers and URL
        url = 'baseUrl/api/'
        # Add API key and format to the payload
        payload['api_key'] = API_KEY
        payload['format'] = 'json'
        todo = status_indicator_service.update()
        response = requests.delete(api_url, json=todo)
        self._logger.debug("Plant has been successfully removed from greenhouse")
        response.json()