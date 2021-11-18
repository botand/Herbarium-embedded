from RPi import GPIO
import busio
import adafruit_ads1x15.ads1115 as ads
from adafruit_ads1x15.analog_in import AnalogIn
from src.utils import get_logger
from src.utils.configuration import config

_SERVICE_TAG = "service.AdcService"
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
        adc_config = config["adc_config"]
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

    def get_water_level_value(self):
        value = self._water_level_channel.voltage
        self._logger.debug(
            f"Water Level : {value} V"
        )
        return value

    def get_ambient_luminosity_value(self):
        value = self._ambient_luminosity_channel.voltage
        self._logger.debug(
            f"Amb. Lum. : {value} V"
        )
        return value

    def get_plant_hygrometry_value(self, plant_nb):

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
        self._logger.debug(
            f"Plant Hygro. ({plant_nb}) : {value} V"
        )
        return value
