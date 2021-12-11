def get_greenhouse_url(uuid):
    """
    Build the URL to retrieve the greenhouse data
    :param uuid Universal unique identifier of the greenhouse
    :type uuid str
    """
    return f"/greenhouse/{uuid}"


def greenhouse_send_data_url(uuid):
    """
    Build the URL to send logs
    :param uuid Universal unique identifier of the greenhouse
    :type uuid str
    """
    return f"/greenhouse/{uuid}/logs"


def greenhouse_notify_added_plant_url(uuid):
    """
    Build the URL to notify the API about a new plant.
    :param uuid Universal unique identifier of the greenhouse
    :type uuid str
    """
    return f"/greenhouse/{uuid}/plant"


def greenhouse_remove_plant_url(uuid):
    """
    Build the URL to notify the API when a plant is removed.
    :param uuid Universal unique identifier of the plant
    :type uuid str
    """
    return f"/plant/{uuid}"
