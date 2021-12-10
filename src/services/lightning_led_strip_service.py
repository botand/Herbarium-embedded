"""Service to interact with the LED Lightning"""
from neopixel import NeoPixel
from src.utils import pin_number_to_digital_gpio, led_utils, get_logger
from src.utils.configuration import config

_SERVICE_TAG = "services.LightningLedStripService"
_CONFIG_TAG = "led_strip"
_LED_COUNT_CONFIG_KEY = "led_count"
_LED_PIN_CONFIG_KEY = "gpio_data_in"
_LED_BY_TILE_KEY = "led_by_tile"


class LightningLedService:
    """
    Service to interact with the LED Lightning
    """
    __instance = None
    _logger = get_logger(_SERVICE_TAG)

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: PumpService
        """
        if LightningLedService.__instance is None:
            LightningLedService.__instance = LightningLedService()
        return LightningLedService.__instance

    def __init__(self):

        light_config = config[_CONFIG_TAG]   
        self._led_count = light_config[_LED_COUNT_CONFIG_KEY]
        self._led_by_tile = light_config[_LED_BY_TILE_KEY]
        self._strip = NeoPixel(
            pin_number_to_digital_gpio(light_config[_LED_PIN_CONFIG_KEY]),
            self._led_count,
            auto_write=False,
        )
        self._logger.info("initialized")
        self.turn_off_all()

    def _update_segment(self, tile_nb, color, brightness):
        """
        Update one selected segment by it number.
        :param tile_nb: number of the tile [0-15]
        :param color: selected color in led_utils.py
        :param brightness: [0.0-100.0]
        """
        for i in range(
            tile_nb * self._led_by_tile, (tile_nb + 1) * self._led_by_tile
        ):
            self._strip[i] = (
                round(color[0] * brightness / 100),
                round(color[1] * brightness / 100),
                round(color[2] * brightness / 100),
            )
        self._strip.show()

    def turn_on(self, tile_nb, brightness):
        """
        Turn ON tile selected lightning
        :param tile_nb: tile number [0-15]
        """
        self._update_segment(tile_nb, led_utils.COLOR_WHITE, brightness)
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
