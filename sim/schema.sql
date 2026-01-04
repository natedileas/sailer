create table if not exists telemetry (
    dt text, -- iso8601
    raw blob
);

create table if not exists command (
    dt text, -- iso8601
    command text
);