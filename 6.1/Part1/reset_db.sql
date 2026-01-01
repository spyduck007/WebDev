DROP TABLE IF EXISTS characters;
CREATE TABLE characters
(
    c_id       INTEGER PRIMARY KEY,
    c_name     TEXT NOT NULL,
    c_wit      INTEGER,
    c_strength INTEGER,
    c_attack   INTEGER,
    c_defense  INTEGER,
    c_magic    INTEGER
);