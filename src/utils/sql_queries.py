"""All SQL queries that can be used in the project"""

# Sensors level
GET_UNTRANSMITTED_SENSORS_DATA = "select * from sensors_data where transmitted=0"
INSERT_TANK_LEVEL = "insert into sensors_data(type, value) values ('T', ?)"
INSERT_MOISTURE_LEVEL_FOR_PLANT = (
    "insert into sensors_data(type, value, plant_uuid) values ('M', ?, ?)"
)
INSERT_AMBIANT_LIGHT = "insert into sensors_data(type, value) values ('L', ?)"
UPDATE_SENSORS_TRANSMITTED_FROM_DATE = (
    "update sensors_data set transmitted=? where timestamp > ?"
)
DELETE_SENSORS_TRANSMITTED = "delete from sensors_data where transmitted=1"

# Actuators orders
GET_UNTRANSMITTED_ACTUATORS_ORDER = "select * from actuactors where transmitted=0"
INSERT_VALVE_ORDER = (
    "insert into actuactors(type, status, plant_uuid) values ('V', ?, ?)"
)
INSERT_LIGHT_STRIP_ORDER = (
    "insert into actuactors(type, status, plant_uuid) values ('L', ?, ?)"
)
INSERT_PUMP_ORDER = "insert into actuactors(type, status) values ('P', ?)"
UPDATE_ACTUATORS_TRANSMITTED_FROM_DATE = (
    "update actuators set transmitted=? where timestamp > ?"
)
DELETE_ACTUATORS_TRANSMITTED = "delete from actuators where transmitted=1"

# Plants
GET_UNTRANSMITTED_PLANT = "select * from plant where transmitted=0"
GET_PLANTS = "select * from plant"
GET_PLANT_BY_POSITION = "select * from plant where position=?"
GET_PLANT_BY_UUID = "select * from plant where uuid=?"
INSERT_NEW_PLANT = "insert into plant(uuid, position) values (?, ?)"
UPDATE_PLANT = "update plant set uuid=?, moisture_goal=?, light_exposure_min_duration=?, transmitted=? where uuid=?"
UPDATE_PLANT_INFO = "update plant set uuid=?, moisture_goal=?, light_exposure_min_duration=? where uuid=?"
UPDATE_PLANT_LEVELS = (
    "update plant set moisture_goal=?, light_exposure_min_duration=? where uuid=?"
)
UPDATE_PLANT_POSITION = "update plant set position=? where uuid=?"
DELETE_PLANT = "delete from plant where uuid=?"
