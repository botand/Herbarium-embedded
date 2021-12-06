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
        self._delta_detection = config[_DELTA_DETECTION]
        self._max_sample_regulation = config[_MAX_SAMPLE_REGULATION]

        # water Shot
        self._shot_duration = config[_SHOT_DURATION]
        self._pump_speed = config[_PUMP_SPEED]
        self._shot_query_queue = []  # Contains plant position line.
        self._query_status = False # False:wating, True:In progress
        self._previous_time = 0

    def hygrometric_update(plants):
        for plant in plants: 

            hygro_val = ADCService.instance().get_plant_hygrometry_value(plant.position())
            cummulative = self._cummulative(plant.position())
            last_read = self._last_read(plant.position())
            average = self._average(plant.position())
            nb_sample = self._nb_sample(plant.position())

            # Si on a détecté une diférence d'hygrométrie spontannée on conjuge avec la dernière mesure 
            # pour confirmer ce changement et détecter l'ajout ou le retrait d'un pot.
            if ((hygro_val <= (average - self._delta_detection)) || (hygro_val >= (average + self._delta_detection))) && 
            ((hygro_val >= (last_read - self._delta_detection)) && (hygro_val <= (last_read + self._delta_detection))):

                # If it was an adding
                if hygro_val >= (average + self._delta_detection)
                    # TODO : aouter dans la dB
                else
                    # TODO : Retirer de la DB

                # Redo the cummulatiive for a new average value
                cummulative = last_read
                nb_sample = 1

            cummulative += hygro_val
            nb_sample += 1
            last_read = hygro_val

            # Hyometric reglation at every MAX SAMPLE BEFORE REGULATION acquisiition cycle
            if nb_sample == self._max_sample_regulation:
                average = cummulative / nb_sample
                if plant.moisture_goal() != None
                    # TODO Send DB
                    # TODO Regulatio procedure
                cummulative = 0
                nb_sample = 0              

        

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
                    

                


