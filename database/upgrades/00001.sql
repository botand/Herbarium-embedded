 -- Creation date: 10 nov 2021

create table if not exists plant
(
    uuid                        TEXT
        primary key,
    position                    INTEGER not null,
    moisture_goal               REAL    default 80.0 not null,
    light_exposure_min_duration REAL    default 14.0 not null,
    planted_at                  INTEGER default (time('now')) not null,
    transmitted                 BOOLEAN default 0 not null,
    check (light_exposure_min_duration >= 0.0 AND light_exposure_min_duration < 24.0),
    check (moisture_goal >= 0.0 AND moisture_goal < 100.0),
    check (position >= 0)
);

create table if not exists actuators
(
    type        TEXT    not null,
    timestamp   INTEGER default (time('now')) not null,
    status      BOOLEAN not null,
    plant_uuid  TEXT
        references plant
            on delete cascade,
    transmitted BOOLEAN default 0 not null,
    check (type in ('V', 'L', 'P'))
);

create table if not exists sensors_data
(
    type        TEXT not null,
    timestamp   INTEGER default (time('now')) not null,
    value       REAL not null,
    plant_uuid  TEXT
        references plant,
    transmitted BOOLEAN default 0 not null,
    check (type in ('M', 'L', 'T'))
);


