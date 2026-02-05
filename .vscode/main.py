import sqlite3

# Define the database file name chosen for your project
DB_FILE = 'airline_data.db'

def get_connection():
    """Helper function to establish a database connection."""
    return sqlite3.connect(DB_FILE)

# --- CLI FUNCTIONS MAPPED TO REQUIREMENTS ---

def add_new_flight():
    """Add a New Flight record to the database."""
    conn = get_connection()
    f_num = input("Enter Flight Number (e.g., BA123): ")
    f_date = input("Enter Departure Date (YYYY-MM-DD): ")
    f_status = input("Enter Status (e.g., Scheduled): ")
    conn.execute("INSERT INTO Flights (flight_num, departure_date, status) VALUES (?, ?, ?)", 
                 (f_num, f_date, f_status))
    conn.commit()
    conn.close()
    print("\n[Success] New flight added.")

def view_flights_by_criteria():
    """Retrieve flights based on multiple criteria like destination, status, or departure date."""
    conn = get_connection()
    
    print("\n--- FILTER FLIGHTS BY ---")
    print("1. Destination City")
    print("2. Flight Status")
    print("3. Departure Date")
    print("4. View All Flights")
    
    choice = input("\nSelect filter criteria (1-4): ")
    
    if choice == '1':
        # Show available destinations
        print("\n--- Available Destinations ---")
        cursor = conn.execute("SELECT DISTINCT city FROM Destinations ORDER BY city")
        cities = [row[0] for row in cursor.fetchall()]
        print(", ".join(cities))
        
        city = input("\nEnter Destination City: ")
        query = """SELECT f.flight_num, d.city, f.status, f.departure_date 
                   FROM Flights f 
                   LEFT JOIN Destinations d ON f.dest_id = d.dest_id 
                   WHERE d.city LIKE ?"""
        cursor = conn.execute(query, (f'%{city}%',))
        
    elif choice == '2':
        # Show available statuses
        print("\n--- Available Statuses ---")
        cursor = conn.execute("SELECT DISTINCT status FROM Flights ORDER BY status")
        statuses = [row[0] for row in cursor.fetchall()]
        print(", ".join(statuses))
        
        status = input("\nEnter Status: ")
        query = """SELECT f.flight_num, d.city, f.status, f.departure_date 
                   FROM Flights f 
                   LEFT JOIN Destinations d ON f.dest_id = d.dest_id 
                   WHERE f.status LIKE ?"""
        cursor = conn.execute(query, (f'%{status}%',))
        
    elif choice == '3':
        # Show available dates
        print("\n--- Available Departure Dates ---")
        cursor = conn.execute("SELECT DISTINCT departure_date FROM Flights ORDER BY departure_date")
        dates = [row[0] for row in cursor.fetchall()]
        print(", ".join(dates))
        
        dep_date = input("\nEnter Departure Date (YYYY-MM-DD): ")
        query = """SELECT f.flight_num, d.city, f.status, f.departure_date 
                   FROM Flights f 
                   LEFT JOIN Destinations d ON f.dest_id = d.dest_id 
                   WHERE f.departure_date LIKE ?"""
        cursor = conn.execute(query, (f'%{dep_date}%',))
        
    elif choice == '4':
        query = """SELECT f.flight_num, d.city, f.status, f.departure_date 
                   FROM Flights f 
                   LEFT JOIN Destinations d ON f.dest_id = d.dest_id"""
        cursor = conn.execute(query)
    else:
        print("Invalid selection.")
        conn.close()
        return
    
    results = cursor.fetchall()
    
    print(f"\n{'='*55}")
    print(f"RESULTS: {len(results)} flight(s) found")
    print(f"{'='*55}")
    print(f"\n{'Flight':<10} | {'Destination':<15} | {'Status':<12} | {'Date'}")
    print("-" * 55)
    
    if results:
        for row in results:
            print(f"{row[0]:<10} | {str(row[1]):<15} | {row[2]:<12} | {row[3]}")
    else:
        print("No flights match your criteria.")
    
    conn.close()

def update_flight_information():
    """Update flight schedules, such as departure time or status."""
    conn = get_connection()
    
    # Show available flights first
    print("\n--- Available Flights ---")
    cursor = conn.execute("SELECT flight_id, flight_num, departure_date, status FROM Flights")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Flight: {row[1]} | Date: {row[2]} | Status: {row[3]}")
    
    try:
        f_id = int(input("\nEnter Flight ID to update: "))
    except ValueError:
        print("Invalid Flight ID. Please enter a number.")
        conn.close()
        return
    
    new_status = input("Enter new status: ")
    new_date = input("Enter new departure date (or leave blank to keep current): ")
    
    if new_date:
        conn.execute("UPDATE Flights SET status = ?, departure_date = ? WHERE flight_id = ?", 
                     (new_status, new_date, f_id))
    else:
        conn.execute("UPDATE Flights SET status = ? WHERE flight_id = ?", (new_status, f_id))
    
    conn.commit()
    
    # Show the updated flight to confirm
    cursor = conn.execute("SELECT flight_num, departure_date, status FROM Flights WHERE flight_id = ?", (f_id,))
    updated = cursor.fetchone()
    
    if updated:
        print(f"\n[Success] Flight {updated[0]} updated!")
        print(f"New Status: {updated[2]} | New Date: {updated[1]}")
    else:
        print("\n[Error] Flight ID not found.")
    
    conn.close()

def assign_pilot_to_flight():
    """Assign a pilot to a flight and manage pilot schedules."""
    conn = get_connection()
    
    # Show available flights
    print("\n--- Available Flights ---")
    cursor = conn.execute("SELECT flight_id, flight_num, departure_date FROM Flights")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Flight: {row[1]} | Date: {row[2]}")
    
    # Show available pilots
    print("\n--- Available Pilots ---")
    cursor = conn.execute("SELECT pilot_id, name FROM Pilots")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Name: {row[1]}")
    
    try:
        f_id = int(input("\nEnter Flight ID: "))
        p_id = int(input("Enter Pilot ID to assign: "))
    except ValueError:
        print("Invalid ID. Please enter numbers only.")
        conn.close()
        return
    
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
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | Name: {row[1]} | License: {row[2]}")
    
    try:
        p_id = int(input("\nEnter Pilot ID to view their assigned flights: "))
    except ValueError:
        print("Invalid Pilot ID. Please enter a number.")
        conn.close()
        return
    
    query = """SELECT f.flight_num, f.departure_date, d.city 
               FROM Flights f 
               JOIN Destinations d ON f.dest_id = d.dest_id 
               WHERE f.pilot_id = ?"""
    cursor = conn.execute(query, (p_id,))
    results = cursor.fetchall()
    
    print(f"\n--- Schedule for Pilot ID {p_id} ---")
    if results:
        for row in results:
            print(f"Flight {row[0]} | Date: {row[1]} | Destination: {row[2]}")
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
        print("5. Back to Main Menu")
        
        choice = input("\nSelect an option (1-5): ")
        
        if choice == '1':
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
        
        elif choice == '2':
            # Add new destination
            add_new_destination(conn)
        
        elif choice == '3':
            # Update destination information
            cursor = conn.execute("SELECT dest_id, airport_code, city FROM Destinations ORDER BY city")
            print("\n--- Available Destinations ---")
            destinations = cursor.fetchall()
            for row in destinations:
                print(f"ID: {row[0]} | Code: {row[1]} | City: {row[2]}")
            
            try:
                d_id = int(input("\nEnter Destination ID to update: "))
            except ValueError:
                print("Invalid ID. Please enter a number.")
                continue
            
            print("\nWhat would you like to update?")
            print("1. City Name")
            print("2. Airport Code")
            update_choice = input("Select (1-2): ")
            
            if update_choice == '1':
                new_city = input("Enter new city name: ")
                conn.execute("UPDATE Destinations SET city = ? WHERE dest_id = ?", (new_city, d_id))
                conn.commit()
                print(f"[Success] Destination city updated to: {new_city}")
            elif update_choice == '2':
                new_code = input("Enter new airport code: ")
                conn.execute("UPDATE Destinations SET airport_code = ? WHERE dest_id = ?", (new_code, d_id))
                conn.commit()
                print(f"[Success] Airport code updated to: {new_code}")
        
        elif choice == '4':
            # Delete a destination
            cursor = conn.execute("SELECT dest_id, airport_code, city FROM Destinations ORDER BY city")
            print("\n--- Available Destinations ---")
            destinations = cursor.fetchall()
            for row in destinations:
                print(f"ID: {row[0]} | Code: {row[1]} | City: {row[2]}")
            
            try:
                d_id = int(input("\nEnter Destination ID to delete: "))
            except ValueError:
                print("Invalid ID. Please enter a number.")
                continue
            
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
        
        elif choice == '5':
            break
        else:
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
        
        if flight_choice == '1':
            # Show available flights
            cursor = conn.execute("SELECT flight_id, flight_num, departure_date, pilot_id FROM Flights ORDER BY flight_id")
            flights = cursor.fetchall()
            print("\n--- Available Flights ---")
            for row in flights:
                print(f"ID: {row[0]} | Flight: {row[1]} | Date: {row[2]} | Pilot ID: {row[3]}")
            
            try:
                f_id = int(input("\nEnter Flight ID to assign: "))
            except ValueError:
                print("Invalid Flight ID.")
                return
            
            # Show available pilots
            cursor = conn.execute("SELECT pilot_id, name FROM Pilots ORDER BY pilot_id")
            pilots = cursor.fetchall()
            print("\n--- Available Pilots ---")
            for row in pilots:
                print(f"ID: {row[0]} | Name: {row[1]}")
            
            try:
                p_id = int(input("\nEnter Pilot ID to assign: "))
            except ValueError:
                print("Invalid Pilot ID.")
                return
            
            # Update flight with new destination and pilot
            conn.execute("UPDATE Flights SET dest_id = ?, pilot_id = ? WHERE flight_id = ?", (new_dest_id, p_id, f_id))
            conn.commit()
            
            # Show confirmation
            cursor = conn.execute("SELECT f.flight_num, p.name FROM Flights f JOIN Pilots p ON f.pilot_id = p.pilot_id WHERE f.flight_id = ?", (f_id,))
            result = cursor.fetchone()
            if result:
                print(f"\n[Success] Flight {result[0]} assigned to {new_city} with Pilot {result[1]}")
        
        elif flight_choice == '2':
            # Create new flight
            flight_num = input("\nEnter flight number (e.g., FL-200): ")
            dep_date = input("Enter departure date (YYYY-MM-DD): ")
            status = input("Enter status (Scheduled/On Time/Delayed/Cancelled): ")
            
            # Show available pilots
            cursor = conn.execute("SELECT pilot_id, name FROM Pilots ORDER BY pilot_id")
            pilots = cursor.fetchall()
            print("\n--- Available Pilots ---")
            for row in pilots:
                print(f"ID: {row[0]} | Name: {row[1]}")
            
            try:
                p_id = int(input("\nEnter Pilot ID to assign: "))
            except ValueError:
                print("Invalid Pilot ID.")
                return
            
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
    
    conn.close()

# --- MAIN CLI MENU ---

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
        print("6. View/Update Destination Information")
        print("7. View Summarised Reports")
        print("8. Exit")
        
        choice = input("\nSelect an option (1-8): ")
        
        if choice == '1': add_new_flight()
        elif choice == '2': view_flights_by_criteria()
        elif choice == '3': update_flight_information()
        elif choice == '4': assign_pilot_to_flight()
        elif choice == '5': view_pilot_schedule()
        elif choice == '6': manage_destination_info()
        elif choice == '7': view_summarised_data()
        elif choice == '8': 
            print("Exiting System...")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main_menu()