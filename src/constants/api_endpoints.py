from turtle import position


def get_greenhouse_url(uuid):
    return f"/greenhouse/{uuid}"


def greenhouse_send_data_url(uuid):
    return f"/greenhouse/{uuid}/logs"


def greenhouse_notify_added_plant_url(uuid):
    return f"/greenhouse/{uuid}/plant/{position}"


def greenhouse_update_plant_detail_url(plant_uuid):
    return f"/greenhouse/plant/{plant_uuid}"


def greenhouse_remove_plant_url(plant_uuid):
    return f"/greenhouse/plant/{plant_uuid}"
