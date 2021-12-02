"""Service to interact with the valves"""
from RPi import GPIO
from src.utils import time_in_millisecond, get_logger

_SERVICE_TAG = "service.ValveService"
_VALVE_SELECTOR_PIN_S0 = "gpio_selector_pin_S0"
_VALVE_SELECTOR_PIN_S1 = "gpio_selector_pin_S1"
_VALVE_SELECTOR_PIN_S2 = "gpio_selector_pin_S2"
_VALVE_SELECTOR_PIN_S3 = "gpio_selector_pin_S3"
_VALVE_PIN_CONFIG_KEY = "gpio_position_out"
_PWM_FREQ = "pwm_freq"
_VALVE_POSITION_OFF = "position_off"
_VALVE_POSITION_ON = "position_on"
_VALVE_OPENING_TIME = "opening_time"
_VALVE_CLOSING_TIME = "closing_time"


class ValveService:
    """
    Service to interact with the valves
    """

    _logger = get_logger(_SERVICE_TAG)

    def __init__(self, config):
        """
        :param config: configuration to use.
        :type config : dict of str
        """

        self._valve_pin = config[_VALVE_PIN_CONFIG_KEY]
        self._valve_s0 = config[_VALVE_SELECTOR_PIN_S0]
        self._valve_s1 = config[_VALVE_SELECTOR_PIN_S1]
        self._valve_s2 = config[_VALVE_SELECTOR_PIN_S2]
        self._valve_s3 = config[_VALVE_SELECTOR_PIN_S3]
        self._pwm_freq = config[_PWM_FREQ]
        self._position = {
            "open": config[_VALVE_POSITION_ON],
            "close": config[_VALVE_POSITION_OFF],
        }
        self._timing = {
            "open": config[_VALVE_OPENING_TIME],
            "close": config[_VALVE_CLOSING_TIME],
        }

        # GPIO Assignation and configuration
        GPIO.setup(self._valve_s0, GPIO.OUT)
        GPIO.setup(self._valve_s1, GPIO.OUT)
        GPIO.setup(self._valve_s2, GPIO.OUT)
        GPIO.setup(self._valve_s3, GPIO.OUT)

        GPIO.setup(self._valve_pin, GPIO.OUT)
        self._valve = GPIO.PWM(self._valve_pin, self._pwm_freq)
        self._valve.start(0)

        # Valve position mechanism
        self._valve_state = (
            []
        )  # actual position for all valves, will be fulled by initializing process
        self._asked_valve_state = []  # wait line of tuple (addr, asked_pos)
        self._is_moving = False
        self._previous_time = time_in_millisecond()

        # Initiate valves
        self._logger.debug(
            "Valve Initialisation - Closing all the vales"
        )
        self.close_all()
        for i in range(16):
            self._valve_state.append("open")
        while self._valve_state[15] != "close":
            self.update()
        self._logger.debug("Valve Initialisation - Done !")

    def _select_addr(self, valve_nb):
        """
        :param valve_nb: decimal selected valve [0-15]
        :type valve_nb: int
        Convert the decimal value into binary and update the GPIO selectors
        """
        bin_valve_nb = "{0:b}".format(valve_nb)

        # number of 0 correction, all number must be on 4 digit
        zero = "0"
        for i in range(4 - len(bin_valve_nb)):
            bin_valve_nb = zero + bin_valve_nb

        if bin_valve_nb[0] == "1":
            GPIO.output(self._valve_s3, GPIO.HIGH)
        else:
            GPIO.output(self._valve_s3, GPIO.LOW)

        if bin_valve_nb[1] == "1":
            GPIO.output(self._valve_s2, GPIO.HIGH)
        else:
            GPIO.output(self._valve_s2, GPIO.LOW)

        if bin_valve_nb[2] == "1":
            GPIO.output(self._valve_s1, GPIO.HIGH)
        else:
            GPIO.output(self._valve_s1, GPIO.LOW)

        if bin_valve_nb[3] == "1":
            GPIO.output(self._valve_s0, GPIO.HIGH)
        else:
            GPIO.output(self._valve_s0, GPIO.LOW)

    def close(self, tile_nb):
        """
        Close selected Valve
        :param tile_nb : tile number [0-15]
        :type tile_nb: int
        """
        self._asked_valve_state.append((tile_nb, "close"))  # Add close request at tail

    def close_all(self):
        """
        Close all valves
        """
        for i in range(16):
            self.close(i)

    def open(self, tile_nb):
        """
        Open Selected Valves
        :param tile_nb : tile number [0-15]
        :type tile_nb: int
        """
        self._asked_valve_state.append((tile_nb, "open"))  # Add open request at tail

    def update(self):
        """
        Update the valves status and apply PWM control
        """
        # is buffer is empty just pass
        if len(self._asked_valve_state) == 0:
            return

        asked_addr = int(self._asked_valve_state[0][0])
        asked_state = self._asked_valve_state[0][1]

        # if the valve is already in the asked position just pass too
        if asked_state == self._valve_state[asked_addr]:
            self._asked_valve_state.pop(0)  # Remove the asked position
            self._logger.debug(
                f"Valve {asked_addr} already in position {asked_state}"
            )
            return

        # if we need to modify the valve position, check time and move !
        actual_time = time_in_millisecond()

        # if it's the first update for the actual movement request, then update previous
        if not self._is_moving:
            self._is_moving = True
            self._previous_time = time_in_millisecond()

        # So if the movement is incomplete
        if actual_time - self._previous_time < self._timing[asked_state]:
            self._select_addr(asked_addr)  # valve selection
            self._valve.ChangeDutyCycle(
                self._position[asked_state]
            )  # update valve movement

        # if the movement is finished
        else:
            self._select_addr(asked_addr)  # valve selection
            self._valve.ChangeDutyCycle(0)  # stop PWM
            self._valve_state[asked_addr] = asked_state  # Update valve movement
            self._asked_valve_state.pop(0)  # Remove the asked position
            self._is_moving = False
            self._logger.debug(
                f"Valve {asked_addr} moved to position {asked_state}"
            )
