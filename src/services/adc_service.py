"""Service to interact with the ADC in order to get Analog Values"""
from math import exp
from RPi import GPIO
import busio
import adafruit_ads1x15.ads1115 as ads
from adafruit_ads1x15.analog_in import AnalogIn
from src.utils import get_logger
from src.utils.configuration import config

_SERVICE_TAG = "service.AdcService"
_CONFIG_TAG = "adc_config"
_I2C_PIN_SDA = "i2c_sda"
_I2C_PIN_SCL = "i2c_scl"
_ADC_CHANNEL_WATER_LEVEL = "adc_channel_water_level"
_ADC_CHANNEL_AMBIENT_LUMINOSITY = "adc_channel_ambient_luminosity"
_ADC_CHANNEL_PLANT_HYGROMETRY = "adc_channel_plant_hygrometry"
_PLANT_HYGROMETRY_SELECTOR_PIN_S0 = "gpio_selector_pin_S0"
_PLANT_HYGROMETRY_SELECTOR_PIN_S1 = "gpio_selector_pin_S1"
_PLANT_HYGROMETRY_SELECTOR_PIN_S2 = "gpio_selector_pin_S2"
_PLANT_HYGROMETRY_SELECTOR_PIN_S3 = "gpio_selector_pin_S3"


class ADCService:
    """
    Service to interact with the ADC in order to get Analog Values
    """
    __instance = None
    _logger = get_logger(_SERVICE_TAG)

    @staticmethod
    def instance():
        """
        Get the service
        :rtype: ADCService
        """
        if ADCService.__instance is None:
            ADCService.__instance = ADCService()
        return ADCService.__instance

    def __init__(self):
        """Initialize the service"""
        adc_config = config[_CONFIG_TAG]
        self._i2c = busio.I2C(adc_config[_I2C_PIN_SCL], adc_config[_I2C_PIN_SDA])
        self._adc = ads.ADS1115(self._i2c)
        self._water_level_channel = AnalogIn(self._adc, adc_config[_ADC_CHANNEL_WATER_LEVEL])
        self._ambient_luminosity_channel = AnalogIn(self._adc, adc_config[_ADC_CHANNEL_AMBIENT_LUMINOSITY])
        self._plant_hygrometry_channel = AnalogIn(self._adc, adc_config[_ADC_CHANNEL_PLANT_HYGROMETRY])

        self._plant_s0 = adc_config[_PLANT_HYGROMETRY_SELECTOR_PIN_S0]
        self._plant_s1 = adc_config[_PLANT_HYGROMETRY_SELECTOR_PIN_S1]
        self._plant_s2 = adc_config[_PLANT_HYGROMETRY_SELECTOR_PIN_S2]
        self._plant_s3 = adc_config[_PLANT_HYGROMETRY_SELECTOR_PIN_S3]
        GPIO.setup(self._plant_s0, GPIO.OUT)
        GPIO.setup(self._plant_s1, GPIO.OUT)
        GPIO.setup(self._plant_s2, GPIO.OUT)
        GPIO.setup(self._plant_s3, GPIO.OUT)
        self._logger.info("initialized")

    def get_water_level_value(self):
        """
        Get water level in percentage
        :return: water level [0-100]
        :rtype float
        In the report we have indicate the water level expression.
        Considering the 0% is 200mL lux and 100% is 1000 mL.
        The absolute minimum is -5% (160mL) and maximum absolute is 120% (1150mL).
        We use a double conversion. First in order to get the water volume.
        Since we use a power serie, it is impossible to have negative number.
        Also the minimum is 200mL but its not the absolute minimum. 
        In that way we can technicaly go below 0% and conserve a better R^2 in the expression.
        """
        value = self._water_level_channel.voltage
        value = 3469 * value ** -2.91
        value = 0.125 * value - 25
        self._logger.debug(
            f"Water Level : {value} %"
        )
        return value

    def get_ambient_luminosity_value(self):
        """
        Get water level in percentage
        :return: luminosity percentage [0-100]
        :rtype float
        In the report we have indicate the luminosity level expression.
        Considering the 0% is 40 lux and 100% is 1000 lux.
        """
        value = self._ambient_luminosity_channel.voltage
        value = 5.08e-9 * exp(8.07 * value)
        self._logger.debug(
            f"Amb. Lum. : {value} %"
        )
        return value

    def get_plant_hygrometry_value(self, plant_nb):
        """
        Get plant hygrometry in percentage.
        If negative, there is no plant hanged.
        :param plant_nb: plant number [0-15]
        :type plant_nb: int
        :return: relative hygrometry [0-100]
        :rtype float
        """

        bin_plant_nb = "{0:b}".format(plant_nb)

        # number of 0 correction, all number must be on 4 digit
        zero = "0"
        for i in range(4 - len(bin_plant_nb)):
            bin_plant_nb = zero + bin_plant_nb

        if bin_plant_nb[0] == "1":
            GPIO.output(self._plant_s3, GPIO.HIGH)
        else:
            GPIO.output(self._plant_s3, GPIO.LOW)

        if bin_plant_nb[1] == "1":
            GPIO.output(self._plant_s2, GPIO.HIGH)
        else:
            GPIO.output(self._plant_s2, GPIO.LOW)

        if bin_plant_nb[2] == "1":
            GPIO.output(self._plant_s1, GPIO.HIGH)
        else:
            GPIO.output(self._plant_s1, GPIO.LOW)

        if bin_plant_nb[3] == "1":
            GPIO.output(self._plant_s0, GPIO.HIGH)
        else:
            GPIO.output(self._plant_s0, GPIO.LOW)

        value = self._plant_hygrometry_channel.voltage
        value = -38.3 * value + 140
        self._logger.debug(
            f"Plant Hygro. ({plant_nb}) : {value} %"
        )
        return value
