"""Controller that manage the luminosity regulation"""
from datetime import datetime
from src.services import (
    ADCService,
    DatabaseService,
    LightningLedService
)
from src.utils.configuration import config
from src.utils import (
    get_logger,
    time_in_millisecond,
)

from src.utils.sql_queries import INSERT_LIGHT_STRIP_ORDER

_CONTROLLER_TAG = "controllers.LuminosityRegulationController"
_CONFIG_TAG = "luminosity"
_PLANT_COUNT = "plant_count"
_TZ_OFFSET = "time_zone_offset"
_INTERVAL_UPDATE = "interval_update"
_TIME_RANGE_CENTER = "time_range_center"


class LuminosityRegulationController:
    """Controller that manage the luminosity regulation"""

    _logger = get_logger(_CONTROLLER_TAG)
    _adc_instance = ADCService.instance()
    _db_instance = DatabaseService.instance()
    _led_instance = LightningLedService.instance()

    def __init__(self):
        """Initialize the Controller"""
        lum_config = config[_CONFIG_TAG]
        self._time_zone_offset = config[_TZ_OFFSET]
        self._update_time = lum_config[_INTERVAL_UPDATE]
        self._time_range_center = lum_config[_TIME_RANGE_CENTER]
        self._previous_time = 0
        self.time = 0
        self._light_state = [False]*16
        self._logger.debug("initialized")

    def update(self, plants):
        """
        Execute the updates:
        for each plant check if it has the required lightning time.
        :param plants: plant list - 16 elements by ASC position
        :type plants: list
        """
        if (time_in_millisecond() - self._previous_time) > self._update_time:
            self._previous_time = time_in_millisecond()

            # What time is it ?
            now = datetime.utcnow()
            hour = (now.hour - self._time_zone_offset) + now.minute / 6

            # Regulation for plants
            for i, plant in enumerate(plants):
                if plant is not None and self._is_on(plant, hour):
                    value = 100 - self._adc_instance.get_ambient_luminosity_value()
                    if value <= 0:
                        value = 0.0
                    elif value >= 100:
                        value = 100.0

                    self._led_instance.turn_on(plant.position, value)
                    self._logger.info(
                        "Turn ON Tile %d Lightning (%d %%)",
                        plant.position, value)
                else:
                    self._led_instance.turn_off(i)
                    self._logger.info("Turn OFF Tile %d Lightning", i)

    def _is_on(self, plant, hour):
        """
        Detect if we need to turn on the lightning
        :param plant: plant list - 16 elements by ASC position
        :type plant: Plant
        :return true if we need to turn on the lights
        :rtype bool
        """

        # Distribute the exposure time around 14h to create the time range
        time_range = (self._time_range_center - plant.light_exposure_min_duration / 2,
                      self._time_range_center + plant.light_exposure_min_duration / 2)

        # if we are in the time range, turn on the lighting.
        if time_range[0] <= hour <= time_range[1] and not self._light_state[plant.position]:
            self._db_instance.execute(INSERT_LIGHT_STRIP_ORDER, parameters=[1, plant.uuid])
            self._light_state[plant.position] = True
            return True
        if self._light_state[plant.position]:
            self._db_instance.execute(INSERT_LIGHT_STRIP_ORDER, parameters=[0, plant.uuid])
            self._light_state[plant.position] = False
        return False
