"""Controller that manage the data synchronization"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
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
    GET_UNTRANSMITTED_PLANT,
    GET_REMOVED_UNTRANSMITTED_PLANT,
    UPDATE_PLANT_LEVELS,
    UPDATE_PLANT_TRANSMITTED,
    time_in_millisecond, INSERT_OR_IGNORE_PLANT,
)

_CONTROLLER_TAG = "controllers.DataSynchronizationController"
_CONFIG_TAG = "data_synchronization_task"
_CONFIG_INTERVAL_TAG = "interval"
_CONFIG_DELAY_TAG = "delay"


class DataSynchronizationController:
    """Controller that manage the data synchronization  for the device"""

    _logger = get_logger(_CONTROLLER_TAG)

    _api_service = ApiService.instance()

    _db_service = DatabaseService.instance()

    _internet_connection_service = InternetConnectionService.instance()

    _send_logs_last_update = 0
    _new_plant_last_update = 0
    _removed_plant_last_update = 0
    _update_local_last_update = 0

    _tasks = []

    def __init__(self, config):
        """Create the controller"""
        self._executor = ThreadPoolExecutor(max_workers=8)

        task_config = config[_CONFIG_TAG]

        functions = {
            "send_logs": self._send_logs,
            "update_data": self._update_local_plants,
            "check_new_plant": self._notify_new_plant,
            "check_removed_plant": self._notify_removed_plant,
        }

        for key, value in functions.items():
            interval = task_config[key][_CONFIG_INTERVAL_TAG] * 1000
            delay = task_config[key][_CONFIG_DELAY_TAG] * 1000

            self._tasks.append(
                {
                    "interval": interval,
                    "last_update": time_in_millisecond() - interval + delay,
                    "function": value,
                }
            )
        # self._logger.debug(self._tasks)
        self._logger.debug("initialized")

    def update(self):
        """Check and update the different API call (if needed)"""

        current_time = time_in_millisecond()
        for task in self._tasks:
            time_elapsed = current_time - task["last_update"]
            if (
                time_elapsed > task["interval"]
                and self._internet_connection_service.last_connection_check
            ):
                self._executor.submit(task["function"])
                task["last_update"] = current_time

    def _send_logs(self):
        """Transmit all the un-transmitted logs from the API"""
        self._logger.info("Start send logs to the API.")
        _sensors_data_raw = self._db_service.execute(
            GET_UNTRANSMITTED_SENSORS_DATA, commit=False
        )
        _sensors_data = []
        _actuators_data_raw = self._db_service.execute(
            GET_UNTRANSMITTED_ACTUATORS_ORDERS, commit=False
        )
        _actuators_data = []

        for data in _sensors_data_raw:
            _sensors_data.append({
                'type': data[0],
                'timestamp': datetime.fromisoformat(data[1]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'value': data[2],
                'plant_uuid': data[3],
            })

        for data in _actuators_data_raw:
            if data[2] == 0:
                value = False
            else:
                value = True
            _actuators_data.append({
                'type': data[0],
                'timestamp': datetime.fromisoformat(data[1]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'value': value,
                'plant_uuid': data[3],
            })

        if self._api_service.send_logs(_sensors_data, _actuators_data):
            if len(_sensors_data) > 0:
                self._db_service.execute(
                    UPDATE_SENSORS_TRANSMITTED_FROM_DATE,
                    parameters=[
                        _sensors_data[0][1],
                        _sensors_data[-1][1],
                    ],
                )
            if len(_actuators_data) > 0:
                self._db_service.execute(
                    UPDATE_ACTUATORS_TRANSMITTED_FROM_DATE,
                    parameters=[
                        _actuators_data[0][1],
                        _actuators_data[-1][1],
                    ],
                )
            self._logger.info("Logs successfully transmitted to the API.")
        else:
            self._logger.info("Logs unsuccessfully transmitted to the API.")

    def _notify_new_plant(self):
        """Notify the API when a new plant is detected"""
        self._logger.info("Start send new plant to the API.")
        new_plant = self._db_service.execute(GET_UNTRANSMITTED_PLANT)

        if len(new_plant) == 0:
            self._logger.info("There is no plant to transmit.")
            return
        new_plant = new_plant[0]

        plant_uuid = self._api_service.add_plant(
            datetime.fromisoformat(new_plant[0]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'), new_plant[1]
        )

        if plant_uuid:
            self._db_service.execute(
                UPDATE_PLANT_TRANSMITTED,
                [
                    plant_uuid,
                    new_plant[1]
                ],
            )
            self._logger.info("Plant successfully transmitted.")
        else:
            self._logger.info("Plant unsuccessfully transmitted.")

    def _notify_removed_plant(self):
        """Notify the API about the plants that was removed"""
        self._logger.info("Start send removed plant to the API.")
        plant = self._db_service.execute(GET_REMOVED_UNTRANSMITTED_PLANT)

        if len(plant) == 0:
            self._logger.info("There is no plant removed to transmit.")
            return
        plant = plant[0]

        if self._api_service.remove_plant(plant[0]):
            self._logger.warn("Removed UUID %s", str(plant))
            self._db_service.execute(UPDATE_PLANT_TRANSMITTED, [plant[0]])
            self._logger.info("Removed plant (%s) was successfully transmitted.")
        else:
            self._logger.info("Removed plant (%s) unsuccessfully transmitted.")

    def _update_local_plants(self):
        """Update the plants data from the API"""
        self._logger.info("Start gathering plants data from the API.")
        plants = self._api_service.get_greenhouse()

        for plant in plants:
            self._db_service.execute(
                INSERT_OR_IGNORE_PLANT,
                parameters=[
                    plant.uuid,
                    plant.moisture_goal,
                    plant.light_exposure_min_duration,
                    plant.position
                ],
            )
            self._db_service.execute(
                UPDATE_PLANT_LEVELS,
                parameters=[
                    plant.moisture_goal,
                    plant.light_exposure_min_duration,
                    plant.uuid,
                ],
            )
        self._logger.info("Gathering plants data from the API was successfully.")

    def stop(self):
        """Stop every current future"""
        self._logger.debug("Stopping controller")
        self._executor.shutdown(wait=True)
        self._logger.debug("Controller stopped")
