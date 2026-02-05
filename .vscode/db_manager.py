import sqlite3
import os

def run_setup():
    # This creates the physical database file
    conn = sqlite3.connect('airline_data.db')
    cursor = conn.cursor()

      # Instead of hardcoding the CREATE TABLE statements, we read them from schema.sql
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(script_dir, 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_script = f.read()
        
        # Execute the SQL code found inside schema.sql
        cursor.executescript(schema_script)
        print("Schema applied successfully from schema.sql")
    except FileNotFoundError:
        print("Error: schema.sql file not found. Make sure it is in the same folder.")
        return

    # Populate with 10 records per table
    pilots = [
        ("Mark Jones", "LIC-1001"),
        ("Jenny Smith", "LIC-1002"),
        ("David Chen", "LIC-1003"),
        ("Sarah Williams", "LIC-1004"),
        ("Michael Brown", "LIC-1005"),
        ("Emma Davis", "LIC-1006"),
        ("James Wilson", "LIC-1007"),
        ("Lisa Anderson", "LIC-1008"),
        ("Robert Taylor", "LIC-1009"),
        ("Maria Garcia", "LIC-1010")
    ]
    cursor.executemany("INSERT OR IGNORE INTO Pilots (name, license_num) VALUES (?,?)", pilots)

    dests = [("London", "LHR"), ("New York", "JFK"), ("Paris", "CDG"), ("Tokyo", "NRT"), ("Dubai", "DXB"),
             ("Sydney", "SYD"), ("Rome", "FCO"), ("Berlin", "BER"), ("Toronto", "YYZ"), ("Singapore", "SIN")]
    cursor.executemany("INSERT OR IGNORE INTO Destinations (city, airport_code) VALUES (?,?)", dests)

    flights = [
        (101, "FL-101", "2026-05-10", "Scheduled", 1, 1),
        (102, "FL-102", "2026-05-10", "On Time", 2, 2),
        (103, "FL-103", "2026-05-11", "Delayed", 3, 3),
        (104, "FL-104", "2026-05-11", "Scheduled", 4, 4),
        (105, "FL-105", "2026-05-12", "Cancelled", 5, 5),
        (106, "FL-106", "2026-05-12", "On Time", 6, 6),
        (107, "FL-107", "2026-05-13", "Scheduled", 7, 7),
        (108, "FL-108", "2026-05-13", "Delayed", 8, 8),
        (109, "FL-109", "2026-05-14", "On Time", 9, 9),
        (110, "FL-110", "2026-05-14", "Scheduled", 10, 10)
    ]
    cursor.executemany("INSERT OR IGNORE INTO Flights (flight_id, flight_num, departure_date, status, pilot_id, dest_id) VALUES (?,?,?,?,?,?)", flights)

    conn.commit()
    conn.close()
    print("Database 'airline_data.db' successfully initialised.")

if __name__ == "__main__":
    run_setup()