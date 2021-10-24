import array
from pybleno import Characteristic, Descriptor


class DeviceIdentityCharacteristic(Characteristic):

    def __init__(self, characteristic_config, device_uuid):
        """

        :param characteristic_config:
        :type characteristic_config: dict
        :param device_uuid:
        :type device_uuid: str
        """
        descriptors = []
        self._device_uuid = device_uuid

        for descriptor in characteristic_config['descriptors']:
            descriptors.append(Descriptor({
                'uuid': descriptor['uuid'],
                'value': descriptor['value']
            }))

        Characteristic.__init__(self, {
            'uuid': characteristic_config['uuid'],
            'properties': ['read'],
            'descriptors': descriptors,
            'value': None
        })

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = array.array('b')
            data.frombytes(self._device_uuid.encode())

            callback(Characteristic.RESULT_SUCCESS, data)
