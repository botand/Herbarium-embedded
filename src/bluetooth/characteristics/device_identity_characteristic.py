from pybleno import Characteristic, Descriptor


class DeviceIdentityCharacteristic(Characteristic):

    def __init__(self, characteristic_config, device_uuid):
        descriptors = []

        for descriptor in characteristic_config['descriptors']:
            descriptors.append(Descriptor({
                'uuid': descriptor['uuid'],
                'value': descriptor['value']
            }))

        Characteristic.__init__(self, {
            'uuid': characteristic_config['uuid'],
            'properties': ['read'],
            'descriptors': descriptors,
            'value': device_uuid
        })
