from pybleno import Characteristic, Descriptor


class DeviceIdentityCharacteristic(Characteristic):

    def __init__(self, characteristic_config, device_uuid):
        Characteristic.__init__(self, {
            'uuid': characteristic_config['uuid'],
            'properties': ['read'],
            'descriptors': [
                Descriptor({
                    'uuid': characteristic_config['service_uuid'],
                    'value': 'Get the device uuid'
                })
            ],
            'value': device_uuid
        })
