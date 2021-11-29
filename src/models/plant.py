import json
from collections import namedtuple
from json import JSONEncoder
from src.services import api_service


class Plant:
    def __init__(self, last_uuid, uuid, position, type):
        self._last_uuid = last_uuid
        # TODO complete

    @staticmethod
    def create_from_json(data):
        json_dictionary = json.loads(data)
        return Plant(**json_dictionary)

    def __str__(self):
        return "<Plant {0}>".format(self._last_uuid)

    plant = Plant.create_from_json(api_service.get_greenhouse_url())
