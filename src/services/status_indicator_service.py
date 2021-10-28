import board
import time
from neopixel import NeoPixel
from rpi_ws281x import Adafruit_NeoPixel
from src.utils import pin_number_to_digital_gpio, time_in_millisecond, led_utils
from src.models import StatusPattern
import logging

_SERVICE_TAG = "StatusIndicatorService - "

_LED_COUNT_CONFIG_KEY = "led_count"
_LED_PIN_CONFIG_KEY = "gpio_data_in"
_MULTI_ANIMATION_MAXIMUM_TIME = "multi_animation_maximum_time"
_INTERVAL_UPDATE = "interval_update"

_SECOND_TO_MILLISECONDS = 1000


class StatusIndicatorService:

    def __init__(self, config):
        """

        :param config: configuration file to use.
        :type config dict of str
        """
        self._ring = NeoPixel(pin_number_to_digital_gpio(config[_LED_PIN_CONFIG_KEY]), config[_LED_COUNT_CONFIG_KEY],
                              auto_write=False)
        self._led_count = config[_LED_COUNT_CONFIG_KEY]
        self._maximum_time_in_display = config[_MULTI_ANIMATION_MAXIMUM_TIME] * _SECOND_TO_MILLISECONDS

        # Dictionary of the animation to play
        self._animations_in_progress = []
        # Index of the animation currently displayed
        self._current_animation_index = None
        self._current_animation_started_at = 0

        # Number of milliseconds between each refresh
        self._interval_update = config[_INTERVAL_UPDATE]
        # Last time the pattern was updated
        self._last_update = 0

        # These variables are used by each animation as they see fit. Please reset them to 0 when changing animation
        self._current_brightness = 0
        self._current_token = 0
        self._current_offset = 0

    def add_status(self, status):
        """
        Add a status pattern to display
        :param status: pattern to add
        :type status: StatusPattern
        :return: void
        """
        if not isinstance(status, StatusPattern):
            raise TypeError("status type must be an StatusPattern")
        if status not in self._animations_in_progress:
            logging.debug(f'{_SERVICE_TAG} adding pattern: {status}')
            self._animations_in_progress.append(status)
            if len(self._animations_in_progress) == 1:
                self._current_animation_index = 0

    def remove_status(self, status):
        """
        Remove a status from display
        :param status: pattern to remove
        :type status: StatusPattern
        :return: void
        """
        if not isinstance(status, StatusPattern):
            raise TypeError("status type must be an StatusPattern")
        logging.debug(f'{_SERVICE_TAG} removing pattern: {status}')
        index_removed = self._animations_in_progress.index(status)
        self._animations_in_progress.pop(index_removed)

        # If the animation playing is the one that removed or is after the one removed, remove 1 to the current index
        if self._current_animation_index >= index_removed:
            self._current_animation_index -= 1

    def update(self):
        """
        Update the status indicator
        :return:
        """
        # No need to do anything
        if self._current_animation_index is None and len(self._animations_in_progress) == 0:
            return

        # No more animation to run but there is still one in play
        if len(self._animations_in_progress) == 0:
            logging.debug(f'{_SERVICE_TAG} turning off ring')
            self._turn_off()
            self._current_animation_index = None

        # Switch to the next animation if needed
        if (time_in_millisecond() - self._current_animation_started_at) > self._maximum_time_in_display and \
                len(self._animations_in_progress) > 1:
            if (self._current_animation_index + 1) < len(self._animations_in_progress):
                self._current_animation_index += 1
            else:
                self._current_animation_index = 0
            logging.debug(f'{_SERVICE_TAG} starting next animation')
            self._current_animation_started_at = time_in_millisecond()
            self._current_brightness = 0
            self._current_token = 0

        if (time_in_millisecond() - self._last_update) > self._interval_update:
            self._update_animation()
            self._last_update = time_in_millisecond()

    def _update_animation(self):
        if self._current_animation_index is None:
            return

        animation = self._animations_in_progress[self._current_animation_index]

        if animation.animation_type == led_utils.SOLID_ANIMATION:
            self._solid_animation(animation)
        elif animation.animation_type == led_utils.BREATHING_ANIMATION:
            self._breathing_animation(animation)

    def _turn_off(self):
        """
        Turn off all the led of the ring.
        :return: void
        """
        self._ring.brightness = 0.0
        self._ring.show()

    def _solid_animation(self, animation):
        """
        Set the same color to all the pixels
        :param animation:
        :type animation StatusPattern
        :return: void
        """
        self._ring.fill(animation.color)
        self._ring.brightness = animation.max_brightness
        self._ring.show()

    def _breathing_animation(self, animation):
        """
        Make the pixels breath in the ring
        :param animation:
        :type animation StatusPattern
        :return: void
        """
        if self._current_brightness >= animation.max_brightness:
            self._current_offset = 1
        elif self._current_brightness <= 0:
            self._current_offset = 0

        self._current_brightness += 0.01 if self._current_offset == 0 else -0.01

        self._ring.fill(animation.color)
        self._ring.brightness = self._current_brightness
        self._ring.show()