class Plant:
    """Object which represent a plant"""

    def __init__(self, uuid, position, moisture_goal, light_exposure_min_duration):
        self._uuid = uuid
        self._position = position
        self._moisture_goal = moisture_goal
        self._light_exposure_min_duration = light_exposure_min_duration

    @property
    def uuid(self):
        """Universal unique identifier of the plant"""
        return self._uuid

    @property
    def position(self):
        """Position of the plant"""
        return self._position

    @property
    def moisture_goal(self):
        """Percentage of moisture targeted for the plant"""
        return self._moisture_goal

    @property
    def light_exposure_min_duration(self):
        """Minimum quantity of light in hours for the plant"""
        return self._light_exposure_min_duration

    @staticmethod
    def create_from_dict(data):
        """
        Instantiate a plant from a dictionary
        :param data all the information about the plant
        :type data: dict
        :return instance of the plant
        :rtype: Plant
        """
        return Plant(
            data["uuid"],
            data["position"],
            data["override_moisture_goal"]
            if "override_moisture_goal" in data
            else data["type"]["moisture_goal"],
            data["override_light_exposure_min_duration"]
            if "override_light_exposure_min_duration" in data
            else data["type"]["light_exposure_min_duration"],
        )
