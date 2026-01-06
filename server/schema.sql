create table if not exists telemetry (dt text, -- iso8601
raw blob);

create table if not exists command (dt text, -- iso8601
command text);

create table if not exists slow (
    dt text,
    -- iso8601
    comm_id text,
    temp real,
    humidity real,
    battery real
);

create table if not exists fast (
    dt text,
    -- iso8601
    comm_id text,
    att_x real,
    att_y real,
    att_z real,
    att_dx real,
    att_dy real,
    att_dz real,
    wind_spd real,
    wind_dir real,
    compass real,
    furl real,
    sheet real,
    rudder real
);

create table if not exists once (
    dt text,
    -- iso8601
    comm_id text,
    mission_id text,
    FURL_MAX real,
    SHEET_FURL real,
    RUDDER_CENTER real,
    RECOVERY_COMM_INTERVAL real,
    MAIN_SLEEP_INTERVAL real,
    PICTURE_INTERVAL real
);

create table if not exists pics (
    dt text real,
    -- iso8601
    comm_id text,
    raw blob,
    base64 blob
);