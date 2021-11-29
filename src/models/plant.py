import json
from collections import namedtuple
from json import JSONEncoder
from src.services import ApiService


class Plant:
    def __init__(self, last_uuid, uuid, position, type):
        self._last_uuid = last_uuid
        # TODO complete

    @staticmethod
    def create_from_dict(data):
        return Plant(data["last_uuid"], data["uuid"])

    def __str__(self):
        return "<Plant {0}>".format(self._last_uuid)
