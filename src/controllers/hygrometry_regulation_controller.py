"""HygrometryRegulationController"""
from src.models import plant
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
    REMOVE_PLANT
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

    __instance = None
    _logger = get_logger(_CONTROLLER_TAG)
    _adc_instance = ADCService.instance()
    _db_instance = DatabaseService.instance()

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: HygrometryRegulationController
        """
        if HygrometryRegulationController.__instance is None:
            HygrometryRegulationController.__instance = HygrometryRegulationController()
        return HygrometryRegulationController.__instance
    
    def __init__(self):
        """Initialize the Controller"""

        hygro_config = config[_CONFIG_TAG]

        # Hygrometry regulation, one value per plant position
        self._cummulative = [0.0]*16
        self._last_read = [0.0]*16
        self._average = [0.0]*16
        self._nb_sample = [0]*16
        self._interval_update = hygro_config[_INTERVAL_UPDATE]
        self._delta_detection = hygro_config[_DELTA_DETECTION]
        self._max_sample_regulation = hygro_config[_MAX_SAMPLE_REGULATION]
        self._previous_read_time = 0

        # water Shot
        self._shot_duration = hygro_config[_SHOT_DURATION]
        self._pump_speed = hygro_config[_PUMP_SPEED]
        self._shot_query_queue = []  # Contains plant position line.
        self._query_status = False # False:wating, True:In progress
        self._previous_shot_time = 0

        # Initialisation
        for i in range(config[_PLANT_COUNT]):
            hygro_value = _adc_instance.get_plant_hygrometry_value(i)
            self._cummulative[i] = hygro_value
            self._last_read[i] = hygro_value 
            self._average[i] = hygro_value
            self._nb_sample[i] = 1

    def update(self, plants):
        """
        Execute the following updates:
        - Check for add or removed plants
        - Check for Hygrometry
        - Give some water shots for hygrometry regulation
        :param plants: plant list - 16 elements by ASC position
        :ptype plants: list
        """
        self._shot_update()

        if time_in_millisecond() - self._previous_read_time > self._interval_update:
            self._hygrometric_update(plants)
            self._previous_read_time = time_in_millisecond()

    def _hygrometric_update(self, plants):
        """
        Check for the added or removed plants and ask for hygrometric regulation
        :param plants: plant list - 16 elements by ASC position but it doesn't matter
        :ptype plants: list
        """
        for plant in plants: 
            i = plant.position()
            hygro_val = _adc_instance.get_plant_hygrometry_value(i)

            # Si on a détecté une diférence d'hygrométrie spontannée on conjuge avec la dernière mesure 
            # pour confirmer ce changement et détecter l'ajout ou le retrait d'un pot.
            # if hygro Val != avergae +/- delta AND hygro_val == last_read +/- delta
            difference_avg = hygro_val - self._average[i]
            difference_last_read = hygro_val - self._last_read[i]
            if ((difference_avg <= -self._delta_detection) || (difference_avg >= self._delta_detection)) && 
            ((difference_last_read >= -self._delta_detection) && (difference_last_read <= self._delta_detection)):

               # If it was an adding
                if hygro_val >= (self._average[i] + self._delta_detection):

                    # Ajouter dans la dB
                    _db_instance.execute(INSERT_NEW_PLANT, i)
                else
                    # Retirer de la DB
                    _db_instance.execute(REMOVE_PLANT, plants(i).uuid(), i)

                # Redo the cummulative for a new average value
                self._cummulative(i) = self._last_read(i)
                self._nb_sample(i) = 1

            self._cummulative(i) += hygro_val
            self._nb_sample(i) += 1
            self._last_read(i) = hygro_val

            # Hyometric reglation at every MAX SAMPLE BEFORE REGULATION acquisiition cycle
            if self._nb_sample[i] == self._max_sample_regulation:
                self._average[i] = self._cummulative[i] / self._nb_sample[i]
                if plant.moisture_goal != None
                    # Dataase Communication
                    _db_instance.execute(INSERT_MOISTURE_LEVEL_FOR_PLANT, self._average[i], plants[i].uuid)
                    # Regulation
                    if self.average(i) < plat.moisture_goal()
                        self._query_shot(i)
                self._cummulative(i) = 0
                self._nb_sample(i) = 0              


    def _query_shot(self, plant_position):
        """
        Add a shot query to the line.
        :param plant_position: plant position [0-15]
        :ptype plant_position: int
        """
        self._shot_query_queue.append(plant_position)
        self._logger.debug(f"{_CONTROLLER_TAG} Shot Plannified for plant {plant_position}")

    def _shot_update(self):
        """
        Execute the shot query line. Each shot is done one by one.
        Must be executed as quickly as possible.
        """
        if len(self._shot_query_queue) > 0:
            if !self._query_status:
                self._previous_shot_time = time_in_millisecond()
                _db_instance.execute(INSERT_VALVE_ORDER, "open", plants(self._shot_query_queue[0]).uuid())
                ValveService.instance().open(self._shot_query_queue[0])
                _db_instance.execute(INSERT_PUMP_ORDER, self._pump_seed)
                PumpService.instance().set_speed(self._pump_seed)
                self._query_status = True
            else:
                if time_in_millisecond() - self._previous_shot_time > self._shot_duration:

                    _db_instance.execute(INSERT_VALVE_ORDER, "close", plants(self._shot_query_queue[0]).uuid)
                    ValveService.instance().close(self._shot_query_queue[0])
                    _db_instance.execute(INSERT_PUMP_ORDER, 0)
                    PumpService.instance().stop()
                    self._query_status = False
                    self._logger.debug(f"{_CONTROLLER_TAG} Shot Done for plant {self._shot_query_queue[0]}")
                    self._shot_query_queue.pop(0)
