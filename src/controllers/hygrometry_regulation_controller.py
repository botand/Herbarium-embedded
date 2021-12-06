"""HygrometryRegulationController"""
from src.services import (
    ADCService,
    PumpService,
    ValveService
)
from src.utils import (
    get_logger,
    time_in_millisecond,
)

_CONTROLLER_TAG = "controllers.HygromertyRegulationController"
# Hygrometric Regulation


# For water shot Attribution
_SHOT_DURATION = "shot_duration"
_PUMP_SPEED = "pump_speed"


class HygrometryRegulationController:
    "Controller That manage the hygrometry Regulation"""

    __instance = None

    _logger = get_logger(_SERVICE_TAG)

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: ADCService
        """
        if HygrometryRegulationController.__instance is None:
            HygrometryRegulationController.__instance = HygrometryRegulationController()
        return HygrometryRegulationController.__instance
    
    def __init__(self, config):
        """
        :param config: configuration to use.
        :type config : dict of str
        """
        # Hygrometry regulation, one value per plant position
        # TODO On a besoins de revenr sur les valeurs à l'initialisation. Peut être inverser la boucle tout simplement.
        self._cummulative = []
        self._last_read = []
        self._average = []
        self._nb_sample = []
    
        # water Shot
        self._shot_duration = config[_SHOT_DURATION]
        self._pump_speed = config[_PUMP_SPEED]
        self._shot_query_queue = []  # Contains plant position line.
        self._query_status = False # False:wating, True:In progress
        self._previous_time = 0

    def hygrometric_update(plants):
        for plant in plants: 

            hygro_val = ADCService.instance().get_plant_hygrometry_value(plant.position)
            cummulative = self._cummulative(plant.position)
            last_read = self._last_read(plant.position)
            average = self._average(plant.position)

            if hygro_val != average && _hygro_val == last_read  # TODO Ajouter la tolérence parce que la ca ne marchera pas
                

        

    def _query_shot(plant_position):
        """
        Add a shot query to the line.
        :param plant_position: plant position [0-15]
        :type plant_position: int
        """
        self._shot_query_queue.append(plant_position)
        self._logger.debug(f"{_SERVICE_TAG} Shot Plannified for plant {plant_position}")

    def shot_update():
        """
        Execute the query line. Each shot is done one by one.
        """
        if len(self._shot_query_queue) > 0:
            if !self._query_status:
                self._previous_time = time_in_millisecond()
                ValveService.instance().open(self._shot_query_queue[0])
                PumpService.instace().set_speed(self._pump_seed)
                self._query_status = True
            else:
                if time_in_millisecond() - self._previoous_time > self._shot_duration:
                    ValveService.instance().close(self._shot_query_queue[0])
                    PumpService.instace().stop()
                    self._query_status = False
                    self._logger.debug(f"{_SERVICE_TAG} Shot Done for plant {self._shot_query_queue[0]}")
                    self._shot_query_queue.pop(0)
                    

                


