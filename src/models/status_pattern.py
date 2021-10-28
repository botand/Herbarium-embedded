class StatusPattern:

    def __init__(self, name, color, animation_type, max_brightness = 1.0):
        """
        Status pattern that can be sent to the [StatusIndicatorService]
        :param name:
        :type name str
        :param color: tuple that represent the color like (R, G, B) with each value between 0 and 255
        :type color tuple of int
        :param animation_type: name of the animation
        :type animation_type: int
        :param max_brightness: maximum brightness that will be used by the animation
        :type max_brightness float
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(color, tuple):
            raise TypeError("Color must be a tuple")
        if not isinstance(animation_type, int):
            raise TypeError("Animation type must be an integer")
        if not isinstance(max_brightness, float):
            raise TypeError("Maximum brightness type must be an float")

        self._name = name
        self._color = color
        self._animation_type = animation_type
        self._max_brightness = max_brightness

    @property
    def name(self):
        """
        Name of the status
        :return: str
        """
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def animation_type(self):
        return self._animation_type

    @property
    def max_brightness(self):
        return self._max_brightness

    def __str__(self) -> str:
        return f'LedAnimation[{self._name} {self._color} {self._animation_type} {self._max_brightness}]'
