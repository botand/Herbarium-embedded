from neopixel import NeoPixel
from src.utils import pin_number_to_digital_gpio , led_utils
from src.models import StatusPattern
import RPi.GPIO as GPIO
import logging

_SERVICE_TAG = "valve - "
_VALVE_PIN_CONFIG_KEY = "gpio_position_out"
_VALVE_POSITION_OFF = "position_off"
_VALVE_POSITION_ON = "position_on"


class ValveService:
    def __init__(self, config):
        self._pos_off = config[_VALVE_POSITION_OFF]
        self._pos_on = config[_VALVE_POSITION_ON]

        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(pin_number_to_digital_gpio(config[_VALVE_PIN_CONFIG_KEY]), GPIO.OUT)
        GPIO.setup(12, GPIO.OUT)
        #self._valve = GPIO.PWM(pin_number_to_digital_gpio(config[_VALVE_PIN_CONFIG_KEY]), 50)
        self._valve = GPIO.PWM(12, 50)
        self._valve.start(0)

    def close_valve(self):
        self._valve.ChangeDutyCycle(0)
        logging.debug("Closing the valve")

    def open_valve(self):
        self._valve.ChangeDutyCycle(10)
        logging.debug("Opening the valve")
