"""Controller that manage the lumnosity regulation"""
from src.models import plant
from datetime import datetime

from src.services import (
    ADCService,
    DatabaseService,
    LightningLedService
)
from src.utils import (
    configuration.config,
    get_logger, 
    time_in_millisecond,
)

from src.utils.sql_queries import INSERT_LIGHT_STRIP_ORDER

_CONTROLLER_TAG = "controllers.LuminosityRegulationController"
_CONFIG_TAG = "luminosity"
_PLANT_COUNT = "plant_count"
_TZ_OFFSET = "time_zone_offfset"
_TIME_RANGE_CENTER = "time_range_center"

class LuminosityRegulationController:
    """Controller that manage the lumnosity regulation"""

    __instance = None
    _logger = get_logger(_CONTROLLER_TAG)
    _adc_instance = ADCService.instance()
    _db_instance = DatabaseService.instance()
    _led_instance = LightningLedService.instance()

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: LuminosityRegulationController
        """
        if LuminosityRegulationController.__instance is None:
            LuminosityRegulationController.__instance = LuminosityRegulationController()
        return LuminosityRegulationController.__instance

    def _init_(self):
        """Initialize the Controller"""
        lum_config = config[_CONFIG_TAG]
        time_zone_offset = config[_TZ_OFFSET]

        self._update_time = lum_config["interval_update"]
        self._time_range_cennter = lum_config["_TIME_RANGE_CENTER"]
        self._previous_time = 0
        self.time = 0


    def update(self,plants):
        """
        Execute the updates:
        for each plant check if it has the required lignthing time.
        :param plants: plant list - 16 elements by ASC position
        :ptype plants: list
        """
        if time_in_millisecond - self._previous_time > self._update_time
            self._previous_time = time_in_millisecond

            # What time is it ?
            d = datetime.utcnow()
            self.hour = (d.hour - self.time_zone_offset) + d.min/6

            # Regulation for plants
            for plant in plants:

                if _is_on(plant, hour):
                    _led_instance.turn_on(plant.position, -_adc_instance.get_ambient_luminosity_value)
                    self._logger.debug(f"{_CONTROLLER_TAG} Turn ON Tile {plant_position} Ligthning ({-_adc_instance.get_ambient_luminosity_value} %)")
                else:
                    _led_instance.turn_off(plant.position)
                    self._logger.debug(f"{_CONTROLLER_TAG} Turn OFF Tile {plant_position} Ligthning")


    def _is_on(self, plant):
        """
        detect if we need to turn on the lighning
        :param plants: plant list - 16 elements by ASC position
        :ptype plants: list
        """

        # Distribute the exposure time arround 14h to create the time range
        time_range = (self._time_range_cennter-plant.light_exposure_min_duration/2, 
        self._time_range_cennter+plant.light_exposure_min_duration/2)

        # if we are in the time range, turn on the lightining.
        if self.hour >= time_range[0] && self.hour <= time_range[1]:
            _db_instance.execute(INSERT_LIGHT_STRIP_ORDER, "on", plants(i).uuid())
            return True
        else:
            _db_instance.execute(INSERT_LIGHT_STRIP_ORDER, "off", plants(i).uuid())
            return False
