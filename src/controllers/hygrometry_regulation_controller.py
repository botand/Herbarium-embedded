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
_INTERVAL_UPDATE = "interval_update"
_DELTA_DETECTION = "delta_detection"
_SHOT_DURATION = "shot_duration"
_PUMP_SPEED = "pump_speed"
_MAX_SAMPLE_REGULATION = "max_sample_before_regulation"


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
        self._interval_update = config[_INTERVAL_UPDATE]
        self._delta_detection = config[_DELTA_DETECTION]
        self._max_sample_regulation = config[_MAX_SAMPLE_REGULATION]
        self._previous_read_time = 0

        # water Shot
        self._shot_duration = config[_SHOT_DURATION]
        self._pump_speed = config[_PUMP_SPEED]
        self._shot_query_queue = []  # Contains plant position line.
        self._query_status = False # False:wating, True:In progress
        self._previous_shot_time = 0

    def update(self, plants):
        """
        Execute the following updates:
        - Check for add or removed plants
        - Check for Hygrometry
        - Give some water shots for hygrometry regulation
        :param plants: plant list - 16 elements by ASC position but it doesn't matter
        :type plants: list
        """
        self._shot_update()

        if time_in_millisecond() - self._previous_read_time < self._interval_update:
            self._hygrometric_update(plants)
            self._previous_read_time = time_in_millisecond()

    def _hygrometric_update(self, plants):
        """
        Check for the added or removed plants and ask for hygrometric regulation
        :param plants: plant list - 16 elements by ASC position but it doesn't matter
        :type plants: list
        """
        for plant in plants: 
            i = plant.position()
            hygro_val = ADCService.instance().get_plant_hygrometry_value(i)

            # Si on a détecté une diférence d'hygrométrie spontannée on conjuge avec la dernière mesure 
            # pour confirmer ce changement et détecter l'ajout ou le retrait d'un pot.
            # if hygro Val != avergae +/- delta AND hygro_val == last_read +/- delta
            if ((hygro_val <= (self._average(i) - self._delta_detection)) || (hygro_val >= (self._average(i) + self._delta_detection))) && 
            ((hygro_val >= (self._last_read(i) - self._delta_detection)) && (hygro_val <= (self._last_read(i) + self._delta_detection))):

                # If it was an adding
                if hygro_val >= (self._average(i) + self._delta_detection)
                    # TODO : aouter dans la dB
                else
                    # TODO : Retirer de la DB

                # Redo the cummulative for a new average value
                self._cummulative(i) = self._last_read(i)
                self._nb_sample(i) = 1

            self._cummulative(i) += hygro_val
            self._nb_sample(i) += 1
            self._last_read(i) = hygro_val

            # Hyometric reglation at every MAX SAMPLE BEFORE REGULATION acquisiition cycle
            if self._nb_sample(i) == self._max_sample_regulation:
                self._average(i) = self._cummulative(i) / self._nb_sample(i)
                if plant.moisture_goal() != None
                    # TODO Send DB
                    # TODO Regulation procedure
                    if self.average(i) < plat.moisture_goal()
                        _query_shot(i)
                self._cummulative(i) = 0
                self._nb_sample(i) = 0              

    def _query_shot(self, plant_position):
        """
        Add a shot query to the line.
        :param plant_position: plant position [0-15]
        :type plant_position: int
        """
        self._shot_query_queue.append(plant_position)
        self._logger.debug(f"{_SERVICE_TAG} Shot Plannified for plant {plant_position}")

    def _shot_update(self):
        """
        Execute the shot query line. Each shot is done one by one.
        Must be executed as quickly as possible.
        """
        if len(self._shot_query_queue) > 0:
            if !self._query_status:
                self._previous_shot_time = time_in_millisecond()
                ValveService.instance().open(self._shot_query_queue[0])
                PumpService.instace().set_speed(self._pump_seed)
                self._query_status = True
            else:
                if time_in_millisecond() - self._previous_shot_time > self._shot_duration:
                    ValveService.instance().close(self._shot_query_queue[0])
                    PumpService.instace().stop()
                    self._query_status = False
                    self._logger.debug(f"{_SERVICE_TAG} Shot Done for plant {self._shot_query_queue[0]}")
                    self._shot_query_queue.pop(0)
