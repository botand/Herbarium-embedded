"""Service to interact with the LED Lightning"""
from neopixel import NeoPixel
from src.utils import pin_number_to_digital_gpio, led_utils, get_logger

_SERVICE_TAG = "services.LightningLedStripService"
_LED_COUNT_CONFIG_KEY = "led_count"
_LED_PIN_CONFIG_KEY = "gpio_data_in"
_LED_BY_TILE_KEY = "led_by_tile"


class LightningLedService:
    """
    Service to interact with the LED Lightning
    """

    _logger = get_logger(_SERVICE_TAG)

    def __init__(self, config):
        """
        :param config: configuration file to use.
        :type config : dict of str
        """
        self._led_count = config[_LED_COUNT_CONFIG_KEY]
        self._led_by_tile = config[_LED_BY_TILE_KEY]
        self._strip = NeoPixel(
            pin_number_to_digital_gpio(config[_LED_PIN_CONFIG_KEY]),
            self._led_count,
            auto_write=False,
        )

    def _update_segment(self, tile_nb, color, brightness):
        """
        Update one selected segment by it number.
        :param tile_nb: number of the tile [0-15]
        :param color: selected color in led_utils.py
        :param brightness: [0.0-1.0]
        """
        for i in range(
            tile_nb * self._led_by_tile, (tile_nb + 1) * self._led_by_tile - 1
        ):
            self._strip[i] = (
                round(color[0] * brightness),
                round(color[1] * brightness),
                round(color[2] * brightness),
            )
        self._strip.show()

    def turn_on(self, tile_nb):
        """
        Turn ON tile selected lightning
        :param tile_nb: tile number [0-15]
        """
        self._update_segment(tile_nb, led_utils.COLOR_WHITE, 1)
        self._logger.debug(f"Turn ON Tile {tile_nb} Lightning")

    def turn_off(self, tile_nb):
        """
        Turn OFF tile selected lightning
        :param tile_nb: tile number [0-15]
        """
        self._update_segment(tile_nb, led_utils.COLOR_WHITE, 0)
        self._logger.debug(f"Turn OFF Tile {tile_nb} Lightning")

    def turn_off_all(self):
        """
        Turn OFF ALL tile lightning
        """
        for i in range(self._led_count):
            self._strip[i] = led_utils.COLOR_BLACK
        self._strip.show()
        self._logger.debug(f"Turn OFF All Tiles Lightning")
