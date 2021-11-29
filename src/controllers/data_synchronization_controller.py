from src.services import ApiService, DatabaseService
from src.utils import get_logger, time_in_millisecond
from src.models import Plant

_CONTROLLER_TAG = "controllers.DataSynchronizationController"


class DataSynchronizationController:
    """DOCSTRING"""  # TODO Complete docstring. C'est la tache "Rapport"

    _logger = get_logger(_CONTROLLER_TAG)

    _api_service = ApiService.instance()
    _db_service = DatabaseService.instance()

    def update(self):
        self._logger.info("Update time!")
        # TODO check time

        # TODO check if it's time to send data to the API
        # TODO If YES: get data to send from the DB -> GET_UNTRANSMITTED_SENSORS_DATA, GET_UNTRANSMITTED_ACTUATORS_ORDERS
        # TODO THEN: Send data to the API
        # TODO THEN: Validate the data have been successfully sent
        # TODO THEN: if YES: Mark "transmitted" the data sent in the DB -> UPDATE_SENSORS_TRANSMITTED_FROM_DATE, UPDATE_ACTUATORS_TRANSMITTED_FROM_DATE

        # TODO check if it's time to retrieve data from the API
        self._update_local_plants()

        # TODO check if there is new plants to send to the API

        # TODO check if there if some plants have been removed

    def _update_local_plants(self):
        plants_data = await self._api_service.get_greenhouse()
        plants = []

        for plant_data in plants_data:
            plants.append(Plant.create_from_dict(plant_data))

        # TODO THEN: Update data in the database -> UPDATE_PLANT_INFO
