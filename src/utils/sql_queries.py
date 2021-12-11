"""All SQL queries that can be used in the project"""

# Sensors level
GET_UNTRANSMITTED_SENSORS_DATA = (
    "select * from sensors_data where transmitted=0 order by timestamp asc"
)
INSERT_TANK_LEVEL = "insert into sensors_data(type, value) values ('T', ?)"
INSERT_MOISTURE_LEVEL_FOR_PLANT = (
    "insert into sensors_data(type, value, plant_uuid) values ('M', ?, ?)"
)
INSERT_AMBIANT_LIGHT = "insert into sensors_data(type, value) values ('L', ?)"
UPDATE_SENSORS_TRANSMITTED_FROM_DATE = (
    "update sensors_data set transmitted=1 where timestamp > ? and timestamp < ?"
)
DELETE_SENSORS_TRANSMITTED = "delete from sensors_data where transmitted=1"

# Actuators orders
GET_UNTRANSMITTED_ACTUATORS_ORDERS = (
    "select * from actuators where transmitted=0 order by timestamp asc"
)
INSERT_VALVE_ORDER = (
    "insert into actuators(type, status, plant_uuid) values ('V', ?, ?)"
)
INSERT_LIGHT_STRIP_ORDER = (
    "insert into actuators(type, status, plant_uuid) values ('L', ?, ?)"
)
INSERT_PUMP_ORDER = "insert into actuators(type, status) values ('P', ?)"
UPDATE_ACTUATORS_TRANSMITTED_FROM_DATE = (
    "update actuators set transmitted=1 where timestamp > ? and timestamp < ?"
)
DELETE_ACTUATORS_TRANSMITTED = "delete from actuators where transmitted=1"

# Plants
GET_UNTRANSMITTED_PLANT = "select planted_at, position from plant where transmitted=0 and removed=0 order by planted_at asc limit 1"
GET_REMOVED_UNTRANSMITTED_PLANT = "select uuid from plant where transmitted=0 and removed=1 order by planted_at asc limit 1"
GET_PLANTS = "select * from plant where removed=0 and uuid is not NULL"
GET_PLANT_BY_POSITION = "select * from plant where position=?"
GET_PLANT_BY_UUID = "select * from plant where uuid=?"
INSERT_NEW_PLANT = "insert into plant(position) values (?)"
UPDATE_PLANT_TRANSMITTED = "update plant set transmitted=1 where uuid=?"
INSERT_OR_IGNORE_PLANT = "insert or ignore into plant(uuid, moisture_goal, light_exposure_min_duration, position, transmitted) values (?, ?, ?, ?, 1)"
UPDATE_PLANT = "update plant set uuid=?, moisture_goal=?, light_exposure_min_duration=?, removed=0, transmitted=1 where position=?"
UPDATE_PLANT_UUID = (
    "update plant set uuid=?, transmitted=1 where position=? and transmitted=0 and removed=0"
)
UPDATE_PLANT_LEVELS = (
    "update plant set moisture_goal=?, light_exposure_min_duration=? where uuid=?"
)
UPDATE_PLANT_POSITION = "update plant set position=?, removed=0 where uuid=?"
REMOVE_PLANT = "update plant set removed=1, transmitted=0 where uuid=?"
DELETE_PLANT_REMOVED_TRANSMITTED = "delete from plant where transmitted=1 and removed=1"
