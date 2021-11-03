import time
from src.utils import pin_number_to_digital_gpio
import RPi.GPIO as GPIO
import logging

_SERVICE_TAG = "valve - "
_VALVE_SELECTOR_PIN_S0 = "gpio_selector_pin_S0"
_VALVE_SELECTOR_PIN_S1 = "gpio_selector_pin_S1"
_VALVE_SELECTOR_PIN_S2 = "gpio_selector_pin_S2"
_VALVE_SELECTOR_PIN_S3 = "gpio_selector_pin_S3"
_VALVE_PIN_CONFIG_KEY = "gpio_position_out"
_PWM_FREQ = "pwm_freq"
_VALVE_POSITION_OFF = "position_off"
_VALVE_POSITION_ON = "position_on"


class ValveService:
    def __init__(self, config):
        """
        :param config: configuration file to use.
        :type config : dict of str
        """

        self._valve_pin = config[_VALVE_PIN_CONFIG_KEY]
        self._valve_S0 = config[_VALVE_SELECTOR_PIN_S0]
        self._valve_S1 = config[_VALVE_SELECTOR_PIN_S1]
        self._valve_S2 = config[_VALVE_SELECTOR_PIN_S2]
        self._valve_S3 = config[_VALVE_SELECTOR_PIN_S3]
        self._pwm_freq = config[_PWM_FREQ]
        self._pos_off = config[_VALVE_POSITION_OFF]
        self._pos_on = config[_VALVE_POSITION_ON]

        # GPIO Assignation and configuration
        GPIO.setup(self._valve_S0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._valve_S1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._valve_S2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._valve_S3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.setup(self._valve_pin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
        self._valve = GPIO.PWM(self._valve_pin, self._pwm_freq)
        self._valve.start(0)

    def _select_valve(self, valve_nb):
        """
        :param valve_nb: decimal selected valve [0-15]
        Convert the decimal value into binary and update the GPIO selectors
        """
        bin_valve_nb = "{0:b}".format(valve_nb)

        #
        if bin_valve_nb[0] == '1':
            GPIO.output(self._valve_S3, GPIO.HIGH)
        else:
            GPIO.output(self._valve_S3, GPIO.LOW)

        if bin_valve_nb[1] == '1':
            GPIO.output(self._valve_S2, GPIO.HIGH)
        else:
            GPIO.output(self._valve_S2, GPIO.LOW)

        if bin_valve_nb[2] == '1':
            GPIO.output(self._valve_S1, GPIO.HIGH)
        else:
            GPIO.output(self._valve_S1, GPIO.LOW)

        if bin_valve_nb[3] == '1':
            GPIO.output(self._valve_S0, GPIO.HIGH)
        else:
            GPIO.output(self._valve_S0, GPIO.LOW)

    def close_valve(self, tile_nb):
        """
        :param tile_nb : decimal selected valve [0-15]
        Set the Valve to closed position.
        Note the sleep needed to wait the valve moved to the right position.
        Then deactivate the valve.
        """
        # valve selection
        self._select_valve(tile_nb)

        # update valve position
        self._valve.ChangeDutyCycle(self._pos_off)
        time.sleep(0.7)
        self._valve.ChangeDutyCycle(0)

        # GPIO cleaning and debug logging
        GPIO.cleanup()
        logging.debug(f'Closing the valve #{tile_nb}()')

    def open_valve(self, tile_nb):
        """
        :param tile_nb : decimal selected valve [0-15]
        Set the Valve to open position.
        Note the sleep needed to wait the valve moved to the right position.
        Then deactivate the valve.
        """
        # valve selection
        self._select_valve(tile_nb)

        # update valve position
        self._valve.ChangeDutyCycle(self._pos_on)
        time.sleep(0.7)
        self._valve.ChangeDutyCycle(0)

        # GPIO cleaning and debug logging
        GPIO.cleanup()
        logging.debug(f'Opening the valve #{tile_nb}()')





