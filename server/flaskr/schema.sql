-- Initialization, use only on reset

DROP TABLE IF EXISTS Devices;
CREATE TABLE Devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT KEY NOT NULL,
    device_key TEXT NOT NULL,
    model TEXT,
    production_date TIMESTAMP
);

DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    openid TEXT KEY NOT NULL,
    sign_up_date TIMESTAMP,
    devices TEXT
);

-- initial data
INSERT INTO Devices (device_id, device_key) VALUES ('test', '123456');
INSERT INTO Devices (device_id, device_key) VALUES ('test_sys', 'abcdef');
INSERT INTO Users (openid, devices) VALUES ('test', 'test');
INSERT INTO Users (openid, devices) VALUES ('test_system', 'test_sys');
