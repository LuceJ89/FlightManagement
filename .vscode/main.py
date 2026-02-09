import sqlite3
import re
import os

from db_manager import run_setup

# Database file
DB_FILE = 'airline_data.db'


def ensure_database_initialised():
    if not os.path.exists(DB_FILE):
        run_setup()

def get_connection():
    """Helper function to establish a database connection."""
    return sqlite3.connect(DB_FILE)

# --- CLI FUNCTIONS --- #

def add_new_flight():
    """Add a New Flight record to the database."""
    print("\n" + "="*40)
    print("   ADD NEW FLIGHT")
    print("="*40)
    print("1. Add a New Flight")
    print("2. Return to Main Menu")
    
    choice = input("\nSelect an option (1-2): ").strip()
    
    match choice:
        case '2':
            return
        case '1':
            pass
        case _:
            print("Invalid selection.")
            return
    
    conn = get_connection()
    
    # Showing current flights so user doesn't duplicate flight numbers
    print("\n--- Current Flights ---")
    cursor = conn.execute("SELECT flight_num FROM Flights ORDER BY flight_num")
    existing_flights = [row[0] for row in cursor.fetchall()]
    if existing_flights:
        print(", ".join(existing_flights))
    else:
        print("No flights currently in the system.")
    
    # Get and validate flight number
    while True:
        f_num = input("\nEnter Flight Number (format: FL-XXX, e.g., FL-101): ").strip()
        
        # Check format: FL-XXX (where XXX are digits)
        if not re.match(r'^FL-\d{3}$', f_num):
            print(f"[Error] Invalid flight number format. Must be FL-XXX (e.g., FL-101)")
            continue
        
        # Check if flight number already exists
        cursor = conn.execute("SELECT flight_num FROM Flights WHERE flight_num = ?", (f_num,))
        if cursor.fetchone():
            print(f"[Error] Flight number '{f_num}' already exists. Please use a different number.")
            continue
        
        # Format is valid and flight number is unique
        break
    
    # Select or add destination
    print("\n--- Destination Selection ---")
    cursor = conn.execute("SELECT dest_id, city, airport_code FROM Destinations ORDER BY city")
    destinations = cursor.fetchall()
    
    if destinations:
        print("Available Destinations:")
        for idx, dest in enumerate(destinations, 1):
            print(f"{idx}. {dest[1]} ({dest[2]})")
        print(f"{len(destinations) + 1}. Add a new destination")
        
        while True:
            try:
                dest_choice = int(input("\nSelect destination (number): "))
                if 1 <= dest_choice <= len(destinations):
                    dest_id = destinations[dest_choice - 1][0]
                    break
                elif dest_choice == len(destinations) + 1:
                    # Add new destination
                    city = input("Enter City Name: ").strip()
                    airport_code = input("Enter Airport Code (e.g., JFK): ").strip().upper()
                    try:
                        cursor = conn.execute("INSERT INTO Destinations (city, airport_code) VALUES (?, ?)", 
                                            (city, airport_code))
                        conn.commit()
                        dest_id = cursor.lastrowid
                        print(f"[Success] New destination '{city}' ({airport_code}) added.")
                        break
                    except sqlite3.IntegrityError:
                        print(f"[Error] Airport code '{airport_code}' already exists.")
                        continue
                else:
                    print("[Error] Invalid selection. Please try again.")
            except ValueError:
                print("[Error] Please enter a valid number.")
    else:
        # No destinations exist, prompt to add one
        print("No destinations available. You must add one first.")
        city = input("Enter City Name: ").strip()
        airport_code = input("Enter Airport Code (e.g., JFK): ").strip().upper()
        try:
            cursor = conn.execute("INSERT INTO Destinations (city, airport_code) VALUES (?, ?)", 
                                (city, airport_code))
            conn.commit()
            dest_id = cursor.lastrowid
            print(f"[Success] New destination '{city}' ({airport_code}) added.")
        except sqlite3.IntegrityError:
            print(f"[Error] Airport code '{airport_code}' already exists.")
            conn.close()
            return
    
    f_date = input("Enter Departure Date (YYYY-MM-DD): ")
    f_status = input("Enter Status (e.g., Scheduled): ")
    conn.execute("INSERT INTO Flights (flight_num, departure_date, status, dest_id) VALUES (?, ?, ?, ?)", 
                 (f_num, f_date, f_status, dest_id))
    conn.commit()
    conn.close()
    print(f"\n[Success] New flight '{f_num}' added.")

def view_flights_by_criteria():
    """Retrieve flights based on multiple criteria like destination, status, or departure date."""
    conn = get_connection()
    
    print("\n--- FILTER FLIGHTS BY ---")
    print("1. Destination City")
    print("2. Flight Status")
    print("3. Departure Date")
    print("4. View All Flights")
    print("5. Go Back to Main Menu")
    
    choice = input("\nSelect filter criteria (1-5): ").strip()
    
    match choice:
        case '1':
            # Show available destinations
            print("\n--- Available Destinations ---")
            cursor = conn.execute("SELECT DISTINCT city FROM Destinations ORDER BY city")
            cities = [row[0] for row in cursor.fetchall()]
            print(", ".join(cities))
            
            city = input("\nEnter Destination City: ")
            query = """SELECT f.flight_num, d.city, f.status, f.departure_date, p.name
                       FROM Flights f
                       LEFT JOIN Destinations d ON f.dest_id = d.dest_id
                       LEFT JOIN Pilots p ON f.pilot_id = p.pilot_id
                       WHERE d.city LIKE ?"""
            cursor = conn.execute(query, (f'%{city}%',))
            
        case '2':
            # Show available statuses
            print("\n--- Available Statuses ---")
            cursor = conn.execute("SELECT DISTINCT status FROM Flights ORDER BY status")
            statuses = [row[0] for row in cursor.fetchall()]
            print(", ".join(statuses))
            
            status = input("\nEnter Status: ")
            query = """SELECT f.flight_num, d.city, f.status, f.departure_date, p.name
                       FROM Flights f
                       LEFT JOIN Destinations d ON f.dest_id = d.dest_id
                       LEFT JOIN Pilots p ON f.pilot_id = p.pilot_id
                       WHERE f.status LIKE ?"""
            cursor = conn.execute(query, (f'%{status}%',))
            
        case '3':
            # Show available dates
            print("\n--- Available Departure Dates ---")
            cursor = conn.execute("SELECT DISTINCT departure_date FROM Flights ORDER BY departure_date")
            dates = [row[0] for row in cursor.fetchall()]
            print(", ".join(dates))
            
            dep_date = input("\nEnter Departure Date (YYYY-MM-DD): ")
            query = """SELECT f.flight_num, d.city, f.status, f.departure_date, p.name
                       FROM Flights f
                       LEFT JOIN Destinations d ON f.dest_id = d.dest_id
                       LEFT JOIN Pilots p ON f.pilot_id = p.pilot_id
                       WHERE f.departure_date LIKE ?"""
            cursor = conn.execute(query, (f'%{dep_date}%',))
            
        case '4':
            query = """SELECT f.flight_num, d.city, f.status, f.departure_date, p.name
                       FROM Flights f
                       LEFT JOIN Destinations d ON f.dest_id = d.dest_id
                       LEFT JOIN Pilots p ON f.pilot_id = p.pilot_id"""
            cursor = conn.execute(query)
        case '5':
            conn.close()
            return
        case _:
            print("Invalid selection.")
            conn.close()
            return
    
    results = cursor.fetchall()
    
    print(f"\n{'='*55}")
    print(f"RESULTS: {len(results)} flight(s) found")
    print(f"{'='*55}")
    print(f"\n{'Flight':<10} | {'Destination':<15} | {'Status':<12} | {'Date':<12} | {'Pilot'}")
    print("-" * 75)
    
    if results:
        for row in results:
            pilot_name = row[4] if row[4] else "Unassigned"
            print(f"{row[0]:<10} | {str(row[1]):<15} | {row[2]:<12} | {row[3]:<12} | {pilot_name}")
    else:
        print("No flights match your criteria.")
    
    conn.close()

def update_flight_information():
    """Update flight schedules, such as departure time, status, or destination."""
    print("\n" + "="*40)
    print("  UPDATE FLIGHT INFORMATION")
    print("="*40)
    print("1. Update a Flight")
    print("2. Return to Main Menu")
    
    choice = input("\nSelect an option (1-2): ").strip()
    
    match choice:
        case '2':
            return
        case '1':
            pass
        case _:
            print("Invalid selection.")
            return
    
    conn = get_connection()
    
    # Show available flights first
    print("\n--- Available Flights ---")
    cursor = conn.execute("SELECT flight_id, flight_num, departure_date, status, dest_id FROM Flights")
    flights = cursor.fetchall()
    
    print(f"\n{'ID':<5} | {'Flight':<10} | {'Date':<12} | {'Status':<12} | {'Destination':<15}")
    print("-" * 70)
    
    for row in flights:
        dest_city = "N/A"
        if row[4]:
            dest_cursor = conn.execute("SELECT city FROM Destinations WHERE dest_id = ?", (row[4],))
            dest_result = dest_cursor.fetchone()
            if dest_result:
                dest_city = dest_result[0]
        print(f"{row[0]:<5} | {row[1]:<10} | {row[2]:<12} | {row[3]:<12} | {dest_city:<15}")
    
    # Get valid Flight ID
    while True:
        try:
            f_id = int(input("\nEnter Flight ID to update (e.g. 110): "))
        except ValueError:
            print("[Error] Invalid Flight ID. Please enter a valid flight ID.")
            continue
        
        # Verify flight exists
        cursor = conn.execute("SELECT flight_num, departure_date, status, dest_id FROM Flights WHERE flight_id = ?", (f_id,))
        flight = cursor.fetchone()
        if not flight:
            print("[Error] Flight ID not found. Please enter a valid Flight ID.")
            continue
        
        break
    
    # Get new status with validation rules
    while True:
        new_status = input("Enter new status (or leave blank to keep current): ").strip()
        if new_status == "":
            new_status = flight[2]  # Keep current status
            break
        elif new_status.isdigit():
            print("[Error] Status should contain letters, not numbers. Please try again.")
            continue
        else:
            break
    
    # Get new departure date with validation
    while True:
        new_date = input("Enter new departure date (YYYY-MM-DD, or leave blank to keep current): ").strip()
        if new_date == "":
            new_date = flight[1]  # Keep current date
            break
        elif not re.match(r'^\d{4}-\d{2}-\d{2}$', new_date):
            print("[Error] Invalid date format. Please use YYYY-MM-DD (e.g., 2026-05-10)")
            continue
        else:
            break
    
    # Get new destination with validation
    print("\n--- Destination Update ---")
    cursor = conn.execute("SELECT dest_id, city, airport_code FROM Destinations ORDER BY city")
    destinations = cursor.fetchall()
    
    new_dest_id = flight[3]  # Default to current destination
    
    if destinations:
        print("Available Destinations:")
        for idx, dest in enumerate(destinations, 1):
            print(f"{idx}. {dest[1]} ({dest[2]})")
        print(f"{len(destinations) + 1}. Add a new destination")
        print(f"{len(destinations) + 2}. Keep current destination")
        
        while True:
            try:
                dest_choice = input("\nSelect destination (or leave blank to keep current): ").strip()
                if dest_choice == "":
                    break  # Keep current destination
                dest_choice = int(dest_choice)
                if 1 <= dest_choice <= len(destinations):
                    new_dest_id = destinations[dest_choice - 1][0]
                    break
                elif dest_choice == len(destinations) + 1:
                    # Add new destination
                    city = input("Enter City Name: ").strip()
                    airport_code = input("Enter Airport Code (e.g., JFK): ").strip().upper()
                    try:
                        cursor = conn.execute("INSERT INTO Destinations (city, airport_code) VALUES (?, ?)", 
                                            (city, airport_code))
                        conn.commit()
                        new_dest_id = cursor.lastrowid
                        print(f"[Success] New destination '{city}' ({airport_code}) added.")
                        break
                    except sqlite3.IntegrityError:
                        print(f"[Error] Airport code '{airport_code}' already exists.")
                        continue
                elif dest_choice == len(destinations) + 2:
                    break  # Don't change destination
                else:
                    print("[Error] Invalid selection. Please enter a valid number.")
            except ValueError:
                print("[Error] Please enter a valid number.")
    else:
        # No destinations exist
        print("No destinations available.")
        add_new = input("Would you like to add a new destination? (yes/no): ").strip().lower()
        if add_new == "yes":
            city = input("Enter City Name: ").strip()
            airport_code = input("Enter Airport Code (e.g., JFK): ").strip().upper()
            try:
                cursor = conn.execute("INSERT INTO Destinations (city, airport_code) VALUES (?, ?)", 
                                    (city, airport_code))
                conn.commit()
                new_dest_id = cursor.lastrowid
                print(f"[Success] New destination '{city}' ({airport_code}) added.")
            except sqlite3.IntegrityError:
                print(f"[Error] Airport code '{airport_code}' already exists.")

    
    # Update the flight
    conn.execute("UPDATE Flights SET status = ?, departure_date = ?, dest_id = ? WHERE flight_id = ?", 
                 (new_status, new_date, new_dest_id, f_id))
    conn.commit()
    
    # Show the updated flight to confirm
    cursor = conn.execute("SELECT flight_num, departure_date, status, dest_id FROM Flights WHERE flight_id = ?", (f_id,))
    updated = cursor.fetchone()
    
    if updated:
        dest_city = "N/A"
        if updated[3]:
            dest_cursor = conn.execute("SELECT city FROM Destinations WHERE dest_id = ?", (updated[3],))
            dest_result = dest_cursor.fetchone()
            if dest_result:
                dest_city = dest_result[0]
        print(f"\n[Success] Flight {updated[0]} updated!")
        print(f"New Status: {updated[2]} | New Date: {updated[1]} | New Destination: {dest_city}")
    else:
        print("\n[Error] Flight ID not found.")
    
    conn.close()

def assign_pilot_to_flight():
    """Assign a pilot to a flight and manage pilot schedules."""
    print("\n" + "="*40)
    print("  ASSIGN PILOT TO FLIGHT")
    print("="*40)
    print("1. Assign a Pilot to a Flight")
    print("2. Return to Main Menu")
    
    choice = input("\nSelect an option (1-2): ").strip()
    
    match choice:
        case '2':
            return
        case '1':
            pass
        case _:
            print("Invalid selection.")
            return
    
    conn = get_connection()
    
    # Show available flights
    print("\n--- Available Flights ---")
    cursor = conn.execute("""SELECT f.flight_id, f.flight_num, f.departure_date, p.name
                           FROM Flights f
                           LEFT JOIN Pilots p ON f.pilot_id = p.pilot_id""")
    flights = cursor.fetchall()
    print(f"{'ID':<5} | {'Flight':<10} | {'Date':<12} | {'Pilot'}")
    print("-" * 60)
    for row in flights:
        pilot_name = row[3] if row[3] else "Unassigned"
        print(f"{row[0]:<5} | {row[1]:<10} | {row[2]:<12} | {pilot_name}")
    
    # Show available pilots
    print("\n--- Available Pilots ---")
    cursor = conn.execute("SELECT pilot_id, name FROM Pilots")
    pilots = cursor.fetchall()
    print(f"{'ID':<5} | {'Name':<20}")
    print("-" * 30)
    for row in pilots:
        print(f"{row[0]:<5} | {row[1]:<20}")
    
    # Validate Flight ID exists
    while True:
        try:
            f_id = int(input("\nEnter Flight ID: "))
        except ValueError:
            print("[Error] Invalid Flight ID. Please enter a valid flight ID.")
            continue

        cursor = conn.execute("SELECT 1 FROM Flights WHERE flight_id = ?", (f_id,))
        if not cursor.fetchone():
            print("[Error] Flight ID not found. Please enter a valid Flight ID.")
            continue

        break

    # Validate Pilot ID exists
    while True:
        try:
            p_id = int(input("Enter Pilot ID to assign: "))
        except ValueError:
            print("[Error] Invalid Pilot ID. Please enter a valid pilot ID.")
            continue

        cursor = conn.execute("SELECT 1 FROM Pilots WHERE pilot_id = ?", (p_id,))
        if not cursor.fetchone():
            print("[Error] Pilot ID not found. Please enter a valid Pilot ID.")
            continue

        break
    
    conn.execute("UPDATE Flights SET pilot_id = ? WHERE flight_id = ?", (p_id, f_id))
    conn.commit()
    
    # Show confirmation
    cursor = conn.execute("SELECT f.flight_num, p.name FROM Flights f JOIN Pilots p ON f.pilot_id = p.pilot_id WHERE f.flight_id = ?", (f_id,))
    result = cursor.fetchone()
    
    if result:
        print(f"\n[Success] Pilot {result[1]} assigned to flight {result[0]}!")
    else:
        print("\n[Error] Could not assign pilot.")
    
    conn.close()

def view_pilot_schedule():
    """Retrieve information about pilot schedules."""
    conn = get_connection()
    
    # Show available pilots first
    print("\n--- Available Pilots ---")
    cursor = conn.execute("SELECT pilot_id, name, license_num FROM Pilots")
    pilots = cursor.fetchall()
    if pilots:
        print(f"{'ID':<5} | {'Name':<20} | {'License':<12}")
        print("-" * 43)
        for row in pilots:
            print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<12}")
    else:
        print("No pilots available.")
    
    while True:
        try:
            p_id = int(input("\nEnter Pilot ID to view their assigned flights: "))
        except ValueError:
            print("[Error] Invalid Pilot ID. Please enter a valid pilot ID.")
            continue

        cursor = conn.execute("SELECT 1 FROM Pilots WHERE pilot_id = ?", (p_id,))
        if not cursor.fetchone():
            print("[Error] Pilot ID not found. Please enter a valid Pilot ID.")
            continue

        break
    
    query = """SELECT f.flight_num, f.departure_date, d.city 
               FROM Flights f 
               JOIN Destinations d ON f.dest_id = d.dest_id 
               WHERE f.pilot_id = ?"""
    cursor = conn.execute(query, (p_id,))
    results = cursor.fetchall()
    
    print(f"\n--- Schedule for Pilot ID {p_id} ---")
    if results:
        print(f"{'Flight':<10} | {'Date':<12} | {'Destination':<15}")
        print("-" * 43)
        for row in results:
            print(f"{row[0]:<10} | {row[1]:<12} | {str(row[2]):<15}")
    else:
        print("No flights assigned to this pilot.")
    
    conn.close()

def manage_destination_info():
    """View and update destination information, add/delete destinations."""
    conn = get_connection()
    
    while True:
        print("\n" + "="*40)
        print("   DESTINATION MANAGEMENT")
        print("="*40)
        print("1. View All Destinations")
        print("2. Add New Destination")
        print("3. Update Destination Information")
        print("4. Delete a Destination")
        print("5. Go Back to Main Menu")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        match choice:
            case '1':
                # View all destinations with flight counts
                cursor = conn.execute("""
                    SELECT d.dest_id, d.airport_code, d.city, COUNT(f.flight_id) as flight_count
                    FROM Destinations d
                    LEFT JOIN Flights f ON d.dest_id = f.dest_id
                    GROUP BY d.dest_id, d.airport_code, d.city
                    ORDER BY d.city
                """)
                destinations = cursor.fetchall()
                print(f"\n{'ID':<5} | {'Code':<8} | {'City':<20} | {'Flights'}")
                print("-" * 50)
                for row in destinations:
                    print(f"{row[0]:<5} | {row[1]:<8} | {row[2]:<20} | {row[3]}")
            
            case '2':
                # Add new destination
                add_new_destination(conn)
            
            case '3':
                # Update destination information
                cursor = conn.execute("SELECT dest_id, airport_code, city FROM Destinations ORDER BY city")
                print("\n--- Available Destinations ---")
                destinations = cursor.fetchall()
                print(f"{'ID':<5} | {'Code':<8} | {'City'}")
                print("-" * 40)
                for row in destinations:
                    print(f"{row[0]:<5} | {row[1]:<8} | {row[2]}")
                
                while True:
                    try:
                        d_id = int(input("\nEnter Destination ID to update: "))
                    except ValueError:
                        print("Invalid ID. Please enter a valid destination ID.")
                        continue

                    cursor = conn.execute("SELECT 1 FROM Destinations WHERE dest_id = ?", (d_id,))
                    if not cursor.fetchone():
                        print("[Error] Destination ID not found. Please enter a valid ID.")
                        continue

                    break
                
                print("\nWhat would you like to update?")
                print("1. City Name")
                print("2. Airport Code")
                update_choice = input("Select (1-2): ")
                
                match update_choice:
                    case '1':
                        new_city = input("Enter new city name: ")
                        conn.execute("UPDATE Destinations SET city = ? WHERE dest_id = ?", (new_city, d_id))
                        conn.commit()
                        print(f"[Success] Destination city updated to: {new_city}")
                    case '2':
                        new_code = input("Enter new airport code: ")
                        conn.execute("UPDATE Destinations SET airport_code = ? WHERE dest_id = ?", (new_code, d_id))
                        conn.commit()
                        print(f"[Success] Airport code updated to: {new_code}")
            
            case '4':
                # Delete a destination
                cursor = conn.execute("SELECT dest_id, airport_code, city FROM Destinations ORDER BY city")
                print("\n--- Available Destinations ---")
                destinations = cursor.fetchall()
                print(f"{'ID':<5} | {'Code':<8} | {'City'}")
                print("-" * 40)
                for row in destinations:
                    print(f"{row[0]:<5} | {row[1]:<8} | {row[2]}")
                
                while True:
                    try:
                        d_id = int(input("\nEnter Destination ID to delete: "))
                    except ValueError:
                        print("Invalid ID. Please enter a valid destination ID.")
                        continue

                    cursor = conn.execute("SELECT 1 FROM Destinations WHERE dest_id = ?", (d_id,))
                    if not cursor.fetchone():
                        print("[Error] Destination ID not found. Please enter a valid ID.")
                        continue

                    break
                
                # Check if destination has flights
                cursor = conn.execute("SELECT COUNT(*) FROM Flights WHERE dest_id = ?", (d_id,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"\n[Warning] This destination has {count} flight(s) assigned.")
                    confirm = input("Delete anyway? (yes/no): ")
                    if confirm.lower() != 'yes':
                        print("Deletion cancelled.")
                        continue
                
                conn.execute("DELETE FROM Destinations WHERE dest_id = ?", (d_id,))
                conn.commit()
                print("[Success] Destination deleted.")
            
            case '5':
                break
            case _:
                print("Invalid selection. Please try again.")
    
    conn.close()


def add_new_destination(conn):
    """Add a new destination and optionally assign a flight/pilot to it."""
    new_city = input("\nEnter new city name: ")
    new_code = input("Enter airport code: ")
    
    # Insert new destination
    cursor = conn.execute("INSERT INTO Destinations (city, airport_code) VALUES (?, ?)", (new_city, new_code))
    conn.commit()
    new_dest_id = cursor.lastrowid
    
    print(f"\n[Success] New destination '{new_city}' ({new_code}) created with ID: {new_dest_id}")
    
    # Ask if user wants to assign flights/pilots
    assign_choice = input("\nWould you like to assign a flight to this destination? (yes/no): ")
    
    if assign_choice.lower() == 'yes':
        print("\n1. Assign an existing flight (override previous destination)")
        print("2. Create a new flight")
        flight_choice = input("Select (1-2): ")
        
        match flight_choice:
            case '1':
                # Show available flights
                cursor = conn.execute("SELECT flight_id, flight_num, departure_date, pilot_id FROM Flights ORDER BY flight_id")
                flights = cursor.fetchall()
                print("\n--- Available Flights ---")
                for row in flights:
                    print(f"ID: {row[0]} | Flight: {row[1]} | Date: {row[2]} | Pilot ID: {row[3]}")
                
                while True:
                    try:
                        f_id = int(input("\nEnter Flight ID to assign: "))
                    except ValueError:
                        print("[Error] Invalid Flight ID. Please enter a valid flight ID.")
                        continue

                    cursor = conn.execute("SELECT 1 FROM Flights WHERE flight_id = ?", (f_id,))
                    if not cursor.fetchone():
                        print("[Error] Flight ID not found. Please enter a valid Flight ID.")
                        continue

                    break
                
                # Show available pilots
                cursor = conn.execute("SELECT pilot_id, name FROM Pilots ORDER BY pilot_id")
                pilots = cursor.fetchall()
                print("\n--- Available Pilots ---")
                for row in pilots:
                    print(f"ID: {row[0]} | Name: {row[1]}")
                
                while True:
                    try:
                        p_id = int(input("\nEnter Pilot ID to assign: "))
                    except ValueError:
                        print("[Error] Invalid Pilot ID. Please enter a valid pilot ID.")
                        continue

                    cursor = conn.execute("SELECT 1 FROM Pilots WHERE pilot_id = ?", (p_id,))
                    if not cursor.fetchone():
                        print("[Error] Pilot ID not found. Please enter a valid Pilot ID.")
                        continue

                    break
                
                # Update flight with new destination and pilot
                conn.execute("UPDATE Flights SET dest_id = ?, pilot_id = ? WHERE flight_id = ?", (new_dest_id, p_id, f_id))
                conn.commit()
                
                # Show confirmation
                cursor = conn.execute("SELECT f.flight_num, p.name FROM Flights f JOIN Pilots p ON f.pilot_id = p.pilot_id WHERE f.flight_id = ?", (f_id,))
                result = cursor.fetchone()
                if result:
                    print(f"\n[Success] Flight {result[0]} assigned to {new_city} with Pilot {result[1]}")
            
            case '2':
                # Create new flight
                while True:
                    flight_num = input("\nEnter flight number (e.g., FL-200): ").strip()
                    if not re.match(r'^FL-\d{3}$', flight_num):
                        print("[Error] Invalid flight number format. Must be FL-XXX (e.g., FL-200)")
                        continue

                    cursor = conn.execute("SELECT 1 FROM Flights WHERE flight_num = ?", (flight_num,))
                    if cursor.fetchone():
                        print(f"[Error] Flight number '{flight_num}' already exists. Please use a different number.")
                        continue

                    break

                while True:
                    dep_date = input("Enter departure date (YYYY-MM-DD): ").strip()
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', dep_date):
                        print("[Error] Invalid date format. Please use YYYY-MM-DD (e.g., 2026-05-10)")
                        continue
                    break

                while True:
                    status = input("Enter status (Scheduled/On Time/Delayed/Cancelled): ").strip()
                    if status == "":
                        print("[Error] Status cannot be blank. Please try again.")
                        continue
                    if status.isdigit():
                        print("[Error] Status should contain letters, not numbers. Please try again.")
                        continue
                    break
                
                # Show available pilots
                cursor = conn.execute("SELECT pilot_id, name FROM Pilots ORDER BY pilot_id")
                pilots = cursor.fetchall()
                print("\n--- Available Pilots ---")
                for row in pilots:
                    print(f"ID: {row[0]} | Name: {row[1]}")
                
                while True:
                    try:
                        p_id = int(input("\nEnter Pilot ID to assign: "))
                    except ValueError:
                        print("[Error] Invalid Pilot ID. Please enter a valid pilot ID.")
                        continue

                    cursor = conn.execute("SELECT 1 FROM Pilots WHERE pilot_id = ?", (p_id,))
                    if not cursor.fetchone():
                        print("[Error] Pilot ID not found. Please enter a valid Pilot ID.")
                        continue

                    break
                
                # Insert new flight
                conn.execute("INSERT INTO Flights (flight_num, departure_date, status, pilot_id, dest_id) VALUES (?, ?, ?, ?, ?)", 
                            (flight_num, dep_date, status, p_id, new_dest_id))
                conn.commit()
                
                print(f"\n[Success] New flight {flight_num} created and assigned to {new_city}")


def view_summarised_data():
    """Summarise data, such as number of flights per destination and per pilot."""
    conn = get_connection()
    
    # Summary 1: Flights per destination
    query1 = """SELECT d.city, COUNT(f.flight_id) 
                FROM Destinations d 
                LEFT JOIN Flights f ON d.dest_id = f.dest_id 
                GROUP BY d.city"""
    print("\n--- Summary: Flights per Destination ---")
    for row in conn.execute(query1):
        print(f"{row[0]}: {row[1]} flight(s)")
    
    # Summary 2: Flights per pilot
    query2 = """SELECT p.name, COUNT(f.flight_id) 
                FROM Pilots p 
                LEFT JOIN Flights f ON p.pilot_id = f.pilot_id 
                GROUP BY p.pilot_id, p.name"""
    print("\n--- Summary: Flights per Pilot ---")
    for row in conn.execute(query2):
        print(f"{row[0]}: {row[1]} flight(s)")

    # Summary 3: Flights by status
    query3 = """SELECT status, COUNT(flight_id)
                FROM Flights
                GROUP BY status
                ORDER BY status"""
    print("\n--- Summary: Flights by Status ---")
    for row in conn.execute(query3):
        print(f"{row[0]}: {row[1]} flight(s)")
    
    conn.close()

#--- MAIN CLI MENU --- #

def main_menu():
    while True:
        print("\n" + "="*30)
        print(" AIRLINE FLIGHT MANAGEMENT ")
        print("="*30)
        print("1. Add a New Flight")
        print("2. View Flights by Criteria")
        print("3. Update Flight Information")
        print("4. Assign Pilot to Flight")
        print("5. View Pilot Schedule")
        print("6. Destination Management")
        print("7. View Summarised Reports")
        print("8. Exit")
        
        choice = input("\nSelect an option (1-8): ")
        
        match choice:
            case '1': add_new_flight()
            case '2': view_flights_by_criteria()
            case '3': update_flight_information()
            case '4': assign_pilot_to_flight()
            case '5': view_pilot_schedule()
            case '6': manage_destination_info()
            case '7': view_summarised_data()
            case '8': 
                print("Exiting System...")
                break
            case _:
                print("Invalid selection. Please try again.")

if __name__ == "__main__":
    ensure_database_initialized()
    main_menu()