from __future__ import print_function, division
from RPi import GPIO
from greenhouse_database import GreenhouseDatabase
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class GreenhouseIndicator(object):
    """need to define the led connection"""
     LED_COLOURS = [
            'white',
            'red',
            'blue',
            'green',
        ]

        LEDS = {
            'white': [13, 9, 27],
            'red': [16, 11, 23],
            'blue': [20, 6, 22],
            'green': [21, 12, 25],
        }


    SENSOR_LOW = 'low'
    SENSOR_OK = 'ok'
    SENSOR_HIGH = 'high'

    def __init__(self, db_path='/home/pi/.greenhouse/greenhouse.db'):
        """
        db_path defaults to /home/pi/.greenhouse/greenhouse.db
        """
        self.db = GreenhouseDatabase(db_path)

        self.target_tank_level_lower = 200
        self.target_tank_level_upper = 900

        self.target_humidity_lower = 60
        self.target_humidity_upper = 85

        self.target_soil = 60

        self.target_light = 60

"""definir led ring color with sensor stauts; this an exemple """
        self.status_colours = {
            self.SENSOR_LOW: 'blue',
            self.SENSOR_OK: 'green',
            self.SENSOR_HIGH: 'red',
        }

        self._setup_gpio()

    @property

    @property
    def humidity(self):
        return self.db.get_sensor_value('humidity')

    @property
    def tank_level(self):
        return self.db.get_sensor_value('tank_level')

    @property
    def soil(self):
        return self.db.get_sensor_value('soil')

    @property
    def light(self):
        return self.db.get_sensor_value('light')



    @property
    def tank_level(self):
        lower = self.target_tank_level_lower
        upper = self.target_tank_level_upper

        if lower <= self.tank_level <= upper:
            return self.SENSOR_OK
        elif self.tank_level < lower:
            return self.SENSOR_LOW
        elif self.tank_level > upper:
            return self.SENSOR_HIGH

    @property
    def humidity_status(self):
        lower = self.target_humidity_lower
        upper = self.target_humidity_upper

        if lower <= self.humidity <= upper:
            return self.SENSOR_OK
        elif self.humidity < lower:
            return self.SENSOR_LOW
        elif self.humidity > upper:
            return self.SENSOR_HIGH

    @property
    def soil_status(self):
        if self.soil > self.target_soil:
            return self.SENSOR_OK
        else:
            return self.SENSOR_LOW


    @property
    def light_status(self):
        if self.light >= self.target_light:
            return self.SENSOR_OK
        else:
            return self.SENSOR_LOW

    def _setup_gpio(self):
        for colour in self.LEDS:
            for led in self.LEDS[colour]:
                GPIO.setup(led, GPIO.OUT)
                GPIO.output(led, False)
"""need to configur how to utrn on/off the ledes; this an exemple """

    def _turn_led_on_or_off(self, colour, index, on_or_off):
        led = self.LEDS[colour][index]
        GPIO.output(led, on_or_off)

    def _turn_led_on(self, colour, index):
        self._turn_led_on_or_off(colour, index, on_or_off=True)

    def _turn_led_off(self, colour, index):
        self._turn_led_on_or_off(colour, index, on_or_off=False)

    def _turn_colour_leds_on_or_off(self, colour, on_or_off):
        leds = self.LEDS[colour]
        for led in range(len(leds)):
            if on_or_off:
                self._turn_led_on(colour, led)
            else:
                self._turn_led_off(colour, led)

    def _turn_colour_leds_on(self, colour):
        self._turn_colour_leds_on_or_off(colour=colour, on_or_off=True)

    def _turn_colour_leds_off(self, colour):
        self._turn_colour_leds_on_or_off(colour=colour, on_or_off=False)

    def _turn_index_leds_on_or_off(self, index, on_or_off):
        for colour in self.LEDS:
            if on_or_off:
                self._turn_led_on(colour, index)
            else:
                self._turn_led_off(colour, index)

    def _turn_index_leds_on(self, index):
        self._turn_index_leds_on_or_off(index=index, on_or_off=True)

    def _turn_index_leds_off(self, index):
        self._turn_index_leds_on_or_off(index=index, on_or_off=False)

    def _turn_all_leds_on_or_off(self, on_or_off):
        for colour in self.LEDS:
            if on_or_off:
                self._turn_colour_leds_on(colour)
            else:
                self._turn_colour_leds_off(colour)

    def _turn_all_leds_on(self):
        self._turn_all_leds_on_or_off(on_or_off=True)

    def _turn_all_leds_off(self):
        self._turn_all_leds_on_or_off(on_or_off=False)

    def turn_leds_on(self, colour=None, index=None):
        """
        Turn LEDs on
        - if colour given, only that colour
        - if index given, only that index
        - if both given, only that LED
        - if neither given, all LEDs

        e.g. turn_leds_on()
        e.g. turn_leds_on(colour='red')
        e.g. turn_leds_on(index=0)
        e.g. turn_leds_on(colour='red', index=0)
        """
        if colour and index is not None:
            self._turn_led_on(colour, index)
        elif colour:
            self._turn_colour_leds_on(colour)
        elif index is not None:
            self._turn_index_leds_on(index)
        else:
            self._turn_all_leds_on()

    def turn_leds_off(self, colour=None, index=None):
        """
        Turn LEDs off
        - if colour given, only that colour
        - if index given, only that index
        - if both given, only that LED
        - if neither given, all LEDs

        e.g. turn_leds_off()
        e.g. turn_leds_off(colour='red')
        e.g. turn_leds_off(index=0)
        e.g. turn_leds_off(colour='red', index=0)
        """
        if colour and index is not None:
            self._turn_led_off(colour, index)
        elif colour:
            self._turn_colour_leds_off(colour)
        elif index is not None:
            self._turn_index_leds_off(index)
        else:
            self._turn_all_leds_off()

    def show_status_on_leds(self):
        """
        Use LEDs to indicate sensor statuses according to self.status_colours
        """
        sensor_statuses = [
            self.tank_level_status,
            self.humidity_status,
            self.soil_status,
            self.light_status,

        ]

        for status in sensor_statuses:
            colour = self.status_colours[status]
            self.turn_leds_on(colour)
            sleep(2)
            self.turn_leds_off(colour)
            sleep(0.1)


def main():
    indicator = GreenhouseIndicator()
    print("Tank_level:")
    print(indicator.tank_level)
    print("Humidity:")
    print(indicator.humidity)
    print("Soil:")
    print(indicator.soil)
    print("Light:")
    print(indicator.light)

    if indicator.tank_level_status == 'ok':
        print("Tank_level ok")
    elif indicator.tank_level_status == 'low':
        print("tank_level_status too low add water")
    elif indicator.tank_level_status == 'high':
        print("tank_level_status too high")

    if indicator.humidity_status == 'ok':
        print("Humidity ok")
    elif indicator.humidity_status == 'low':
        print("Humidity too low ")
    elif indicator.humidity_status == 'high':
        print("Humidity too high")

    if indicator.humidity_status == 'ok':
        print("Soil ok")
    else:
        print("Soil too dry")

    if indicator.light_status == 'ok':
        print("Light ok")
    else:
        print("Light not ok")

    while True:
        indicator.show_status_on_leds()
        sleep(5)

if __name__ == '__main__':
    main()
