from src.services import (
    ApiService,
    DatabaseService,
    InternetConnectionService,
)
from src.utils import (
    get_logger,
    GET_UNTRANSMITTED_SENSORS_DATA,
    GET_UNTRANSMITTED_ACTUATORS_ORDERS,
    UPDATE_SENSORS_TRANSMITTED_FROM_DATE,
    UPDATE_ACTUATORS_TRANSMITTED_FROM_DATE,
    UPDATE_PLANT_INFO,
    GET_UNTRANSMITTED_PLANT,
    UPDATE_PLANT_TRANSMITTED_UUID,
)
import schedule

_CONTROLLER_TAG = "controllers.DataSynchronizationController"


class DataSynchronizationController:
    # TODO Complete docstring. C'est la tache "Rapport"
    """Controller that manage the data synchronization  for the device"""

    _logger = get_logger(_CONTROLLER_TAG)

    _api_service = ApiService.instance()

    _db_service = DatabaseService.instance()

    _last_update = 0

    def __init__(self):
        """Create the controller"""
        self._logger.debug("Start initialization")
        self._internet_connection_service = InternetConnectionService.instance()

    def update(self):
        self._logger.info("Update time!")
        # TODO check time
        # TODO check if it's time to send data to the API

        # TODO If YES: get data to send from the DB -> GET_UNTRANSMITTED_SENSORS_DATA, GET_UNTRANSMITTED_ACTUATORS_ORDERS
        _sensors_data = self._db_service.execute(GET_UNTRANSMITTED_SENSORS_DATA)
        _actuators_data = self._db_service.execute(GET_UNTRANSMITTED_ACTUATORS_ORDERS)

        # TODO THEN: Send data to the API
        schedule.every(10).minutes.do(
            self._api_service.send_logs(_sensors_data, _actuators_data)
        )

        if self._api_service.send_logs(_sensors_data, _actuators_data):
            self._db_service.execute(
                UPDATE_SENSORS_TRANSMITTED_FROM_DATE,
                parameters=[
                    _sensors_data[0]["timestamp"],
                    _sensors_data[-1]["timestamp"],
                ],
            )
            self._db_service.execute(
                UPDATE_ACTUATORS_TRANSMITTED_FROM_DATE,
                parameters=[
                    _actuators_data[0]["timestamp"],
                    _actuators_data[-1]["timestamp"],
                ],
            )
            self._logger.info("Logs successfully transmitted to the API.")

        # TODO check if it's time to retrieve data from the API
        schedule.every(15).minutes.do(self._update_local_plants())

        # TODO check if there is new plants to send to the API
        plant = self._db_service.execute(GET_UNTRANSMITTED_PLANT)

        plant_uuid = self._api_service.add_plant(plant["planted_at"], plant["position"])

        if plant_uuid:
            self._db_service.execute(
                UPDATE_PLANT_TRANSMITTED_UUID, [plant_uuid, plant["uuid"]]
            )

        # TODO check if there if some plants have been removed
        schedule.every(30).minutes.do(self._api_service.remove_plant())

    def _update_local_plants(self):
        plants = self._api_service.get_greenhouse()

        for plant in plants:
            self._db_service.execute(
                UPDATE_PLANT_INFO,
                parameters=[plant.moisture_goal, plant.light_exposure_min_duration],
            )
