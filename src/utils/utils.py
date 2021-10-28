import time
import board


def pin_number_to_digital_gpio(pin):
    """

    :param pin:
    :type pin: int
    :return:
    """

    pins = [
        board.D0, board.D1, board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8, board.D9,
        board.D10, board.D11, board.D12, board.D13, board.D14, board.D15, board.D16, board.D17, board.D18, board.D19,
        board.D20, board.D21, board.D22, board.D23, board.D24, board.D25, board.D26, board.D27
    ]

    return pins[pin]


def time_in_millisecond():
    """
    Current time in millisecond

    :return: epoch in millisecond
    :rtype: int
    """
    return round(time.time() * 1000)