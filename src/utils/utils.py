"""Contains utils functions"""
import time
import uuid
import board

def pin_number_to_digital_gpio(pin):
    """
    Convert a number into a digital GPIO
    :param pin: number of the GPIO
    :type pin: int
    :return: GPIO Pin
    :rtype: Pin
    """

    pins = [
        board.D0,
        board.D1,
        board.D2,
        board.D3,
        board.D4,
        board.D5,
        board.D6,
        board.D7,
        board.D8,
        board.D9,
        board.D10,
        board.D11,
        board.D12,
        board.D13,
        board.D14,
        board.D15,
        board.D16,
        board.D17,
        board.D18,
        board.D19,
        board.D20,
        board.D21,
        board.D22,
        board.D23,
        board.D24,
        board.D25,
        board.D26,
        board.D27,
    ]

    return pins[pin]

def time_in_millisecond():
    """
    Current time in millisecond

    :return epoch in millisecond
    :rtype: int
    """
    return round(time.time() * 1000)

def generate_uuid_string():
    """
    Generate a new UUID.

    :return a new UUID.
    :rtype: str
    """
    return str(uuid.uuid4())

"GET = Retrieve an existing resource."
HTTP_GET = "GET"
"POST = Create a new resource."
HTTP_POST = "POST"
"PUT = Update an existing resource."
HTTP_PUT = "PUT"
"DELETE = Delete a resource."
HTTP_DELETE = "DELETE"
