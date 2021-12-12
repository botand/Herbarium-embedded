"""HygrometryRegulationController"""
from src.models import StatusPattern
from src.services import (
    ADCService,
    DatabaseService,
    PumpService,
    ValveService, StatusIndicatorService
)
from src.utils.configuration import config
from src.utils import (
    get_logger,
    time_in_millisecond, led_utils,
)
from src.utils.sql_queries import (
    INSERT_MOISTURE_LEVEL_FOR_PLANT,
    INSERT_NEW_PLANT,
    REMOVE_PLANT, INSERT_VALVE_ORDER, INSERT_PUMP_ORDER, INSERT_TANK_LEVEL
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
_HIGH_LEVEL_ALARM_DURATION = "high_level_alarm_duration"


class HygrometryRegulationController:
    """Controller That manage the hygrometry Regulation"""

    _logger = get_logger(_CONTROLLER_TAG)
    _adc_service = ADCService.instance()
    _valve_service = ValveService.instance()
    _pump_service = PumpService.instance()
    _db_service = DatabaseService.instance()
    _status_indicator_service = StatusIndicatorService.instance()
    _empty_water_status_pattern = StatusPattern(
        "low_water_pattern",
        led_utils.COLOR_BLUE,
        led_utils.BLINKING_ANIMATION,
        0.3,
    )
    _low_water_status_pattern = StatusPattern(
        "low_water_pattern",
        led_utils.COLOR_BLUE,
        led_utils.BREATHING_ANIMATION,
        0.3,
    )
    _high_water_status_pattern = StatusPattern(
        "low_water_pattern",
        led_utils.COLOR_RED,
        led_utils.BLINKING_ANIMATION,
        0.3,
    )

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
        self._index_counter = 0

        # Water Level
        self._water_lvl = 0
        self._empty_water_status = False
        self._high_water_status = False
        self._previous_water_db_update = 0
        self._previous_time_high_water = 0
        self._high_level_alarm_duration = hygro_config[_HIGH_LEVEL_ALARM_DURATION]

        # water Shot
        self._shot_duration = hygro_config[_SHOT_DURATION]
        self._pump_speed = hygro_config[_PUMP_SPEED]
        self._shot_query_queue = []  # Contains plant position line.
        self._query_status = False  # False:waiting, True:In progress
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
        - Check for Water Level
        - Check for add or removed plants
        - Check for Hygrometry
        - Give some water shots for hygrometry regulation
        :param plants: plant list - 16 elements by ASC position
        :type plants: list of Plant
        """
        self._water_level_update()
        self._shot_update(plants)
        self._valve_service.update()

        if time_in_millisecond() - self._previous_read_time > self._interval_update:
            self._hygrometry_update(plants[self._index_counter])
            self._index_counter = (self._index_counter + 1) % 16
            self._previous_read_time = time_in_millisecond()

    def _hygrometry_update(self, plant):
        """
        Check for the added or removed plants and ask for hygrometry regulation
        :param plant: actual Plant
        :type plant: Plant
        """

        hygro_val = self._adc_service.get_plant_hygrometry_value(self._index_counter)
        self._logger.debug(f"Pot : {self._index_counter} - Val: {hygro_val}% - Plant : {plant}")

        # Si on a détecté une diférence d'hygrométrie spontannée on conjuge avec la dernière mesure
        # pour confirmer ce changement et détecter l'ajout ou le retrait d'un pot.
        # if hygro Val != avergae +/- delta AND hygro_val == last_read +/- delta
        difference_avg = abs(hygro_val - self._average[self._index_counter])
        difference_last_read = abs(hygro_val - self._last_read[self._index_counter])

        if (difference_avg >= self._delta_detection) and (difference_last_read <= self._delta_detection):

            self._logger.debug(
                f"Plant detection - hygro_val : {hygro_val}% - AVG : {self._average[self._index_counter]}%")
            # If it was an adding
            if (hygro_val > self._average[self._index_counter]) and plant is None:
                # Add to DB
                self._db_service.execute(INSERT_NEW_PLANT, parameters=[self._index_counter])
                self._logger.info("New plant at position %d detected", self._index_counter)
            else:
                if plant is not None:
                    # Remove from DB
                    self._db_service.execute(REMOVE_PLANT, parameters=[plant.uuid])
                    self._logger.info("Plant (%s) removal detected", plant.uuid)
                    self._shot_query_queue.remove(plant.position)

            # Redo the cumulative for a new average value
            self._cummulative[self._index_counter] = self._last_read[self._index_counter]
            self._nb_sample[self._index_counter] = 1
            self._average[self._index_counter] = self._cummulative[self._index_counter] / \
                self._nb_sample[self._index_counter]

        self._cummulative[self._index_counter] += hygro_val
        self._nb_sample[self._index_counter] += 1
        self._last_read[self._index_counter] = hygro_val

        # Hygrometric regulation at every MAX SAMPLE BEFORE REGULATION acquisition cycle
        if self._nb_sample[self._index_counter] == self._max_sample_regulation:
            self._average[self._index_counter] = self._cummulative[self._index_counter] / \
                                                 self._nb_sample[self._index_counter]
            if plant is not None:
                # Database Communication
                self._db_service.execute(INSERT_MOISTURE_LEVEL_FOR_PLANT,
                                         parameters=[self._average[self._index_counter], plant.uuid])
                self._logger.info("Registering moisture level %d%% for %s at position %d ",
                                  self._average[self._index_counter], plant.uuid, plant.position)
                # Regulation
                if self._average[self._index_counter] < plant.moisture_goal:
                    self._query_shot(self._index_counter)
            self._cummulative[self._index_counter] = 0
            self._nb_sample[self._index_counter] = 0

    def _query_shot(self, plant_position):
        """
        Add a shot query to the line.
        :param plant_position: plant position [0-15]
        :type plant_position: int
        """
        self._shot_query_queue.append(plant_position)
        self._logger.info("Querying shot for plant at position %d", plant_position)

    def _shot_update(self, plants):
        """
        Execute the shot query line. Each shot is done one by one.
        Must be executed as quickly as possible.
        :param plants: plant list - 16 elements by ASC position, but it doesn't matter
        :type plants: list of Plant
        """

        if len(self._shot_query_queue) > 0 and not self._empty_water_status:
            if not self._query_status:
                self._previous_shot_time = time_in_millisecond()
                self._db_service.execute(INSERT_VALVE_ORDER, parameters=[1, plants[self._shot_query_queue[0]].uuid])
                self._valve_service.open(self._shot_query_queue[0])
                self._db_service.execute(INSERT_PUMP_ORDER, [1])
                self._pump_service.set_speed(self._pump_speed)
                self._query_status = True
            elif (time_in_millisecond() - self._previous_shot_time) > self._shot_duration:
                self._db_service.execute(INSERT_VALVE_ORDER, parameters=[0, plants[self._shot_query_queue[0]].uuid])
                self._valve_service.close(self._shot_query_queue[0])
                self._db_service.execute(INSERT_PUMP_ORDER, parameters=[0])
                self._pump_service.stop()
                self._query_status = False
                self._logger.debug(f"Shot Done for plant {self._shot_query_queue[0]}")
                self._shot_query_queue.pop(0)

    def _water_level_update(self):
        """
        Check the water Level, block the shot if low water level and update the ring led for different states.
        C'est très compliqué pour rien mais bon c'est sur les bon conseils de mon ami Xavier ;)
        """
        self._water_lvl = self._adc_service.get_water_level_value()
        if (time_in_millisecond() - self._previous_water_db_update) > self._interval_update*1200:
            self._db_service.execute(INSERT_TANK_LEVEL, parameters=[self._water_lvl])
            self._logger.info(f"Water Level : {self._water_lvl} %")
            self._previous_water_db_update = time_in_millisecond()

        if not self._query_status:
            if self._water_lvl <= 0 and not self._empty_water_status:
                self._logger.warning(f"Tank Empty")
                self._empty_water_status = True
                self._status_indicator_service.remove_status(self._low_water_status_pattern)
                self._status_indicator_service.add_status(self._empty_water_status_pattern)
            elif self._water_lvl <= 20 and not self._empty_water_status:
                self._status_indicator_service.add_status(self._low_water_status_pattern)
            elif self._water_lvl >= 25:
                if self._empty_water_status:
                    self._logger.info(f"Refill")
                self._empty_water_status = False
                self._status_indicator_service.remove_status(self._empty_water_status_pattern)
                self._status_indicator_service.remove_status(self._low_water_status_pattern)

            if self._water_lvl >= 100 and not self._high_water_status:
                self._logger.warning(f"High Level Reach")
                self._high_water_status = True
                self._status_indicator_service.add_status(self._high_water_status_pattern)
                self._previous_time_high_water = time_in_millisecond()

            if self._water_lvl < 90 and self._high_water_status:
                self._high_water_status = False

        if self._high_water_status and ((time_in_millisecond() - self._previous_time_high_water) > self._high_level_alarm_duration):
            self._status_indicator_service.remove_status(self._high_water_status_pattern)
