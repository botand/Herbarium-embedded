"""Service to interact with the pump"""
from RPi import GPIO
from src.utils import get_logger
from src.utils.configuration import config

_SERVICE_TAG = "services.PumpService"
_CONFIG_TAG = "pump"
_PUMP_PIN_CONFIG_KEY = "gpio_speed_out"
_PWM_FREQ = "pwm_freq"
_MAX_SPEED = "max_speed"
_MIN_SPEED = "min_speed"


class PumpService:
    """
    Service to interact with the pump
    """
    __instance = None
    _logger = get_logger(_SERVICE_TAG)

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: PumpService
        """
        if PumpService.__instance is None:
            PumpService.__instance = PumpService()
        return PumpService.__instance

    def __init__(self):
        """Initialize the service"""
        pump_config = config[_CONFIG_TAG]
        self._pump_pin = pump_config[_PUMP_PIN_CONFIG_KEY]
        self._pwm_freq = pump_config[_PWM_FREQ]
        self._max_speed = pump_config[_MAX_SPEED]
        self._min_speed = pump_config[_MIN_SPEED]

        GPIO.setup(self._pump_pin, GPIO.OUT)
        self._pump = GPIO.PWM(self._pump_pin, self._pwm_freq)
        self._pump.start(0)

        self._pwm_val = 0.0
        self._logger.debug(f"{_SERVICE_TAG} Pump Initiated")

    def _speed_to_pwm(self, speed):
        """
        Convert speed into pwm percentage
        :param speed: in percentage [0.0-100.0]
        :type speed: double
        """
        return speed * ((self._max_speed - self._min_speed) / 100.0) + self._min_speed

    def set_speed(self, speed):
        """
        Define the speed of the pump and applies it.
        :param speed: in percentage [0.0-100.0]
        :type speed: double
        """
        if speed == 0.0:
            self.stop()
        elif speed == 100:
            self.full_speed()
        else:
            self._pump.ChangeDutyCycle(self._speed_to_pwm(speed))
            self._logger.debug(f"{_SERVICE_TAG} Pump at {speed}%")

    def stop(self):
        """
        Stop the pump.
        """
        self._pump.ChangeDutyCycle(0)
        self._logger.debug(f"{_SERVICE_TAG} Pump stopped")

    def full_speed(self):
        """
        Set Pump at 100% speed.
        """
        self._pump.ChangeDutyCycle(self._max_speed)
        self._logger.debug(f"{_SERVICE_TAG} Pump at full speed")
