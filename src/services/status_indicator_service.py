import board
from neopixel import NeoPixel
from rpi_ws281x import Adafruit_NeoPixel
from src.utils import pin_number_to_digital_gpio
import logging

_SERVICE_TAG = "StatusIndicatorService - "

_LED_COUNT_CONFIG_KEY = "led_count"
_LED_PIN_CONFIG_KEY = "gpio_data_in"


class StatusIndicatorService:

    def __init__(self, config):
        """

        :param config: configuration file to use.
        :type config Array
        """
        self._ring = NeoPixel(pin_number_to_digital_gpio(config[_LED_PIN_CONFIG_KEY]), config[_LED_COUNT_CONFIG_KEY],
                              auto_write=False)
        self._led_count = config[_LED_COUNT_CONFIG_KEY]

    def fill(self, color, brightness=1.0):
        """
        Fill the complete
        :param color: RGB color to apply. Value are between 0 and 255.
        :type color: tuple
        :param brightness: brightness of the ring.
        :type brightness: float
        :return:
        """
        self._ring.fill(color)
        self._ring.show()
