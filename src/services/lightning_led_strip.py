from neopixel import NeoPixel
from src.utils import pin_number_to_digital_gpio, time_in_millisecond, led_utils
from src.models import StatusPattern
import logging

_SERVICE_TAG = "LightningLedStripService - "
_LED_COUNT_CONFIG_KEY = "led_count"
_LED_PIN_CONFIG_KEY = "gpio_data_in"
_LED_BY_TILE_KEY = "led_by_tile"


class LightningLed:
    def __init__(self, config):
        """

        :param config:
        """
        self._led_count = config[_LED_COUNT_CONFIG_KEY]
        self._led_by_tile = config[_LED_BY_TILE_KEY]
        self._strip = NeoPixel(pin_number_to_digital_gpio(config[_LED_PIN_CONFIG_KEY]), self._led_count,
                              auto_write=False)

    def _update_segment(self, tile_nb, color, brightness):
        for i in range(tile_nb*self._led_by_tile-self._led_by_tile, tile_nb*self._led_by_tile):
            self._strip[i] = (round(color[0]*brightness),
                              round(color[1]*brightness),
                              round(color[2]*brightness))
            logging.debug(f"{_SERVICE_TAG} LED {tile_nb} : ({self._strip[i](0)}, "
                          f"{self._strip[i](1)}, {self._strip[i](2)})")

    def turn_on(self, tile_nb):
        logging.debug(f"{_SERVICE_TAG} Turn ON Tile {tile_nb} Lightning")
        self._update_segment(tile_nb, led_utils.COLOR_WHITE, 1)

    def turn_off(self, tile_nb):
        logging.debug(f"{_SERVICE_TAG} Turn OFF Tile {tile_nb} Lightning")
        self._update_segment(tile_nb, led_utils.COLOR_WHITE, 0)

    def turn_off_all(self):
        for i in range(self._led_count):
            self._strip[i] = led_utils.COLOR_BLACK
        logging.debug(f"{_SERVICE_TAG} Turn OFF All Tiles Lightning")

