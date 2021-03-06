"""HygrometryRegulationController"""
from src.services import (
    ADCService,
    DatabaseService,
    PumpService,
    ValveService
)
from src.utils.configuration import config
from src.utils import (
    get_logger,
    time_in_millisecond,
)
from src.utils.sql_queries import (
    INSERT_MOISTURE_LEVEL_FOR_PLANT,
    INSERT_NEW_PLANT,
    REMOVE_PLANT, INSERT_VALVE_ORDER, INSERT_PUMP_ORDER
)

_CONTROLLER_TAG = "controllers.HygromertyRegulationController"
_CONFIG_TAG = "hygrometry"
_PLANT_COUNT = "plant_count"

# Hygrometric Regulation
_INTERVAL_UPDATE = "interval_update"
_DELTA_DETECTION = "delta_detection"
_MAX_SAMPLE_REGULATION = "max_sample_before_regulation"

# For water shot Attribution
_SHOT_DURATION = "shot_duration"
_PUMP_SPEED = "pump_speed"


class HygrometryRegulationController:
    """Controller That manage the hygrometry Regulation"""

    _logger = get_logger(_CONTROLLER_TAG)
    _adc_service = ADCService.instance()
    _valve_service = ValveService.instance()
    _pump_service = PumpService.instance()
    _db_service = DatabaseService.instance()

    def __init__(self):
        """Initialize the Controller"""

        hygro_config = config[_CONFIG_TAG]

        # Hygrometry regulation, one value per plant position
        self._cummulative = [0.0] * 16
        self._last_read = [0.0] * 16
        self._average = [0.0] * 16
        self._nb_sample = [0] * 16
        self._interval_update = hygro_config[_INTERVAL_UPDATE]
        self._delta_detection = hygro_config[_DELTA_DETECTION]
        self._max_sample_regulation = hygro_config[_MAX_SAMPLE_REGULATION]
        self._previous_read_time = 0

        # water Shot
        self._shot_duration = hygro_config[_SHOT_DURATION]
        self._pump_speed = hygro_config[_PUMP_SPEED]
        self._shot_query_queue = []  # Contains plant position line.
        self._query_status = False  # False:wating, True:In progress
        self._previous_shot_time = 0

        # Initialisation
        for i in range(config[_PLANT_COUNT]):
            hygro_value = self._adc_service.get_plant_hygrometry_value(i)
            self._cummulative[i] = hygro_value
            self._last_read[i] = hygro_value
            self._average[i] = hygro_value
            self._nb_sample[i] = 1
        self._logger.debug("initialized")

    def update(self, plants):
        """
        Execute the following updates:
        - Check for add or removed plants
        - Check for Hygrometry
        - Give some water shots for hygrometry regulation
        :param plants: plant list - 16 elements by ASC position
        :type plants: list of Plant
        """
        self._shot_update(plants)

        if time_in_millisecond() - self._previous_read_time > self._interval_update:
            self._hygrometric_update(plants)
            self._previous_read_time = time_in_millisecond()

    def _hygrometric_update(self, plants):
        """
        Check for the added or removed plants and ask for hygrometric regulation
        :param plants: plant list - 16 elements by ASC position, but it doesn't matter
        :type plants: list of Plant
        """
        for plant in plants:
            i = plant.position
            hygro_val = self._adc_service.get_plant_hygrometry_value(i)

            # Si on a d??tect?? une dif??rence d'hygrom??trie spontann??e on conjuge avec la derni??re mesure 
            # pour confirmer ce changement et d??tecter l'ajout ou le retrait d'un pot.
            # if hygro Val != avergae +/- delta AND hygro_val == last_read +/- delta
            difference_avg = hygro_val - self._average[i]
            difference_last_read = hygro_val - self._last_read[i]
            if ((difference_avg <= -self._delta_detection) or (difference_avg >= self._delta_detection)) and (
                    (difference_last_read >= -self._delta_detection) and (
                    difference_last_read <= self._delta_detection)):

                # If it was an adding
                if hygro_val >= (self._average[i] + self._delta_detection):
                    # Add to DB
                    self._db_service.execute(INSERT_NEW_PLANT, [i])
                else:
                    # Remove from DB
                    self._db_service.execute(REMOVE_PLANT, [plants[i].uuid, i])

                # Redo the cumulative for a new average value
                self._cummulative[i] = self._last_read[i]
                self._nb_sample[i] = 1

            self._cummulative[i] += hygro_val
            self._nb_sample[i] += 1
            self._last_read[i] = hygro_val

            # Hygrometric regulation at every MAX SAMPLE BEFORE REGULATION acquisition cycle
            if self._nb_sample[i] == self._max_sample_regulation:
                self._average[i] = self._cummulative[i] / self._nb_sample[i]
                if plant.moisture_goal is not None:
                    # Database Communication
                    self._db_service.execute(INSERT_MOISTURE_LEVEL_FOR_PLANT, [self._average[i], plants[i].uuid])
                    # Regulation
                    if self._average[i] < plant.moisture_goal:
                        self._query_shot(i)
                self._cummulative[i] = 0
                self._nb_sample[i] = 0

    def _query_shot(self, plant_position):
        """
        Add a shot query to the line.
        :param plant_position: plant position [0-15]
        :type plant_position: int
        """
        self._shot_query_queue.append(plant_position)
        self._logger.debug("Shot planned for plant %d", plant_position)

    def _shot_update(self, plants):
        """
        Execute the shot query line. Each shot is done one by one.
        Must be executed as quickly as possible.
        :param plants: plant list - 16 elements by ASC position, but it doesn't matter
        :type plants: list of Plant
        """
        if len(self._shot_query_queue) > 0:
            if not self._query_status:
                self._previous_shot_time = time_in_millisecond()
                self._db_service.execute(INSERT_VALVE_ORDER, [1, plants[self._shot_query_queue[0]].uuid])
                self._valve_service.open(self._shot_query_queue[0])
                self._db_service.execute(INSERT_PUMP_ORDER, [1])
                self._pump_service.set_speed(self._pump_speed)
                self._query_status = True
            elif (time_in_millisecond() - self._previous_shot_time) > self._shot_duration:
                self._db_service.execute(INSERT_VALVE_ORDER, [0, plants[self._shot_query_queue[0]].uuid])
                self._valve_service.close(self._shot_query_queue[0])
                self._db_service.execute(INSERT_PUMP_ORDER, [0])
                self._pump_service.stop()
                self._query_status = False
                self._logger.debug(f"{_CONTROLLER_TAG} Shot Done for plant {self._shot_query_queue[0]}")
                self._shot_query_queue.pop(0)
