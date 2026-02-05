-- Schema for Airline Flight Management

-- 1. Pilots Table: Stores static pilot data
CREATE TABLE IF NOT EXISTS Pilots (
    pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    license_num TEXT UNIQUE NOT NULL
);

-- 2. Destinations Table: Stores airport and city information
CREATE TABLE IF NOT EXISTS Destinations (
    dest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_code TEXT UNIQUE NOT NULL,
    city TEXT NOT NULL
);

-- 3. Flights Table: The central relational table linking Pilots and Destinations
CREATE TABLE IF NOT EXISTS Flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_num TEXT NOT NULL,
    departure_date TEXT NOT NULL,
    status TEXT NOT NULL,
    pilot_id INTEGER,
    dest_id INTEGER,
    -- Establishing Foreign Key Constraints to maintain referential integrity
    FOREIGN KEY (pilot_id) REFERENCES Pilots(pilot_id),
    FOREIGN KEY (dest_id) REFERENCES Destinations(dest_id)
);