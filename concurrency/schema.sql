CREATE TABLE IF NOT EXISTS user_counter (
    user_id INTEGER PRIMARY KEY,
    counter BIGINT NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 0
);

INSERT INTO user_counter (user_id, counter, version)
VALUES (1, 0, 0)
ON CONFLICT (user_id) DO NOTHING;

