"""Service to interact with the status indicator"""
from neopixel import NeoPixel
from src.utils.configuration import config
from src.utils.logger import get_logger
from src.utils import (
    pin_number_to_digital_gpio,
    time_in_millisecond,
    led_utils,
)
from src.models import StatusPattern

_SERVICE_TAG = "services.StatusIndicatorService"
_CONFIG_TAG = "status_indicator"
_LED_COUNT_CONFIG_KEY = "led_count"
_LED_PIN_CONFIG_KEY = "gpio_data_in"
_MULTI_ANIMATION_MAXIMUM_TIME = "multi_animation_maximum_time"
_INTERVAL_UPDATE = "interval_update"

_BREATHING_ANIMATION_STEP = 0.02

_SECOND_TO_MILLISECONDS = 1000


class StatusIndicatorService:
    """
    Service to interact with the status indicator
    """

    __instance = None

    _logger = get_logger(_SERVICE_TAG)

    # pylint: disable=too-many-instance-attributes

    # List of the animation to play
    _animations_in_progress = []

    # Number of milliseconds between each refresh
    _interval_update = 0

    # Last time the pattern was updated
    _last_update = 0

    # These variables are used by each animation as they see fit.
    # Please reset them to 0 when changing animation
    _current_brightness = 0
    _current_token = 0
    _current_offset = 0

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: StatusIndicatorService
        """
        if StatusIndicatorService.__instance is None:
            StatusIndicatorService.__instance = StatusIndicatorService()
        return StatusIndicatorService.__instance

    def __init__(self):
        """Initialize the service"""
        ring_config = config[_CONFIG_TAG]
        self._ring = NeoPixel(
            pin_number_to_digital_gpio(ring_config[_LED_PIN_CONFIG_KEY]),
            ring_config[_LED_COUNT_CONFIG_KEY],
            auto_write=False,
        )
        self._led_count = ring_config[_LED_COUNT_CONFIG_KEY]
        self._maximum_time_in_display = (
            ring_config[_MULTI_ANIMATION_MAXIMUM_TIME] * _SECOND_TO_MILLISECONDS
        )

        # Index of the animation currently displayed
        self._current_animation_index = None
        self._current_animation_started_at = 0

        self._interval_update = ring_config[_INTERVAL_UPDATE]
        self._last_update = 0
        self._logger.info("initialized")

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
            self._logger.debug("adding pattern: %s", status)
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
        try:
            index_removed = self._animations_in_progress.index(status)
        except ValueError:
            return
        self._logger.debug("removing pattern: %s", status)
        self._animations_in_progress.pop(index_removed)

        # If the animation playing is the one that removed or is after the one removed,
        # remove 1 to the current index
        if self._current_animation_index >= index_removed:
            self._current_animation_index -= 1

    def update(self):
        """
        Update the status indicator
        :return:
        """
        # No need to do anything
        if (
            self._current_animation_index is None
            and len(self._animations_in_progress) == 0
        ):
            return

        # No more animation to run but there is still one in play
        if len(self._animations_in_progress) == 0:
            self.turn_off()
            self._current_animation_index = None

        new_animation = False

        # Switch to the next animation if needed
        time_passed = time_in_millisecond() - self._current_animation_started_at
        if (
            time_passed > self._maximum_time_in_display
            and len(self._animations_in_progress) > 1
        ):
            if (self._current_animation_index + 1) < len(self._animations_in_progress):
                self._current_animation_index += 1
            else:
                self._current_animation_index = 0
            self._logger.debug("starting next animation")
            self._current_animation_started_at = time_in_millisecond()
            self._current_brightness = 0
            self._current_token = 0
            self._current_offset = 0
            new_animation = True

        if (time_in_millisecond() - self._last_update) > self._interval_modifier(
            new_animation
        ):
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
        elif animation.animation_type == led_utils.BLINKING_ANIMATION:
            self._blinking_animation(animation)
        elif animation.animation_type == led_utils.SPINNING_ANIMATION:
            self._spinning_animation(animation)
        elif animation.animation_type == led_utils.THEATRE_CHASE_ANIMATION:
            self._theatre_chase_animation(animation)

        # Update the pixels
        self._ring.show()

    def turn_off(self):
        """
        Turn off all the led of the ring.
        :return: void
        """
        self._logger.debug("turning off ring")
        self._ring.brightness = 0.0
        self._ring.show()

    def _solid_animation(self, animation):
        """
        Set the same color to all the pixels
        :param animation: pattern to apply
        :type animation StatusPattern
        :return: void
        """
        self._ring.fill(animation.color)
        self._ring.brightness = animation.max_brightness

    def _breathing_animation(self, animation):
        """
        Make the pixels breath in the ring
        :param animation: patter to apply
        :type animation StatusPattern
        :return: void
        """
        if self._current_brightness >= animation.max_brightness:
            self._current_offset = 1
        elif self._current_brightness <= 0:
            self._current_offset = 0

        self._current_brightness += (
            _BREATHING_ANIMATION_STEP
            if self._current_offset == 0
            else -_BREATHING_ANIMATION_STEP
        )

        self._ring.fill(animation.color)
        self._ring.brightness = self._current_brightness

    def _blinking_animation(self, animation):
        """
        Make the status indicator blink
        :param animation: pattern to apply
        :type animation StatusPattern
        """
        self._current_offset = self._current_offset == 0

        if self._current_offset == 1:
            self._ring.fill(animation.color)
            self._ring.brightness = animation.max_brightness
        else:
            self._ring.brightness = 0

    def _spinning_animation(self, animation):
        """
        Spin the pixels of the indicator
        :param animation: pattern to apply
        :type animation StatusPattern
        """
        self._ring.brightness = animation.max_brightness

        for i in range(self._led_count):
            color = led_utils.COLOR_BLACK
            if i == self._current_offset:
                color = animation.color
            self._ring[i] = color

        self._current_offset += 1
        if self._current_offset >= self._led_count:
            self._current_offset = 0

    def _theatre_chase_animation(self, animation):
        """
        Spin the pixels of the indicator
        :param animation: pattern to apply
        :type animation StatusPattern
        """
        self._ring.brightness = animation.max_brightness

        for i in range(self._led_count):
            if (self._current_token == 0 and i <= self._current_offset) or (
                self._current_token == 1 and i >= self._current_offset
            ):
                color = animation.color
            else:
                color = led_utils.COLOR_BLACK
            self._ring[i] = color

        self._current_offset += 1
        if self._current_offset >= self._led_count:
            self._current_offset = 0
            self._current_token = self._current_token == 0

    def _interval_modifier(self, new_animation=False):
        """
        Determine the interval between each update based on the animation
        :return: number of millisecond that need to be elapsed between update
        :rtype: int
        """
        pattern = self._animations_in_progress[self._current_animation_index]
        modifier = 1
        if pattern.animation_type == led_utils.SOLID_ANIMATION:
            modifier = 10000
        elif pattern.animation_type == led_utils.BREATHING_ANIMATION:
            modifier = 10
        elif pattern.animation_type == led_utils.BLINKING_ANIMATION:
            modifier = 50
        elif pattern.animation_type == led_utils.SPINNING_ANIMATION:
            modifier = 5
        elif pattern.animation_type == led_utils.THEATRE_CHASE_ANIMATION:
            modifier = 10

        return round(self._interval_update * modifier) if new_animation is False else 1
