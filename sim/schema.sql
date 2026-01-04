create table telemetry (
    date text, -- iso8601
    raw blob,
);

create table command (
    date text, -- iso8601
    command text
);