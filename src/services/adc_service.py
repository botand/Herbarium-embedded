"""Service to interact with the ADC - Deviendra une classe Abstraite"""
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(28, 27)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)
print(chan.value, chan.voltage)