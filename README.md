# FlightManagement

Airline Flight Management System

A robust, Python-based Command Line Interface (CLI) application integrated with an SQLite3 relational database. This system is designed to manage airline operations, including flight scheduling, pilot assignments, and destination management.

Features:
Guided Data Entry: Instead of memorising ID numbers, the system provides numbered lists of pilots and destinations to ensure ease of use and data accuracy.

Robust Validation:
Uses Regular Expressions (Regex) to enforce flight number formats (e.g., FL-101) and date formats (YYYY-MM-DD).

Prevents duplicate flight numbers and duplicate airport codes.
Validates that status updates do not contain numeric values.

Relational Integrity:
Enforces Foreign Key relationships between Pilots, Destinations, and Flights.
Includes a "Safe Delete" mechanism that prevents deleting destinations that have active flights assigned to them.

Operational Reporting:
Generates summarised reports using SQL aggregation (GROUP BY, COUNT).
Tracks flight density per destination, pilot workloads, and operational status (Delayed, On Time, etc.).

Safe Navigation: Sub-menus in critical sections (Add, Update, Assign) allow users to return to the Main Menu without making accidental changes, by selecting 2 (return to main menu).

File Structure:
Main.py: The primary application file containing the CLI menu and the logic for interacting with the database.

db_manager.py: The setup script used to initialise the database, read the schema, and seed the tables with initial sample data.

schema.sql: The Data Definition Language (DDL) file containing the SQL blueprints for the Pilots, Destinations, and Flights tables.

airline_data.db: The SQLite database file (generated automatically upon setup).

Installation & Setup:
Clone the repository or download the project files into a single folder.
Ensure Python 3.x is installed on your system.
Initialize the Database: Run the following command to create the database file and populate it with sample data:
Bash

python db_manager.py
Run the Application: Launch the management system by running:
Bash

python Main.py
Database Schema

The system utilises three normalised tables:

Pilots: pilot_id (PK), name, license_num.
Destinations: dest_id (PK), city, airport_code.
Flights: flight_id (PK), flight_num, departure_date, status, pilot_id (FK), dest_id (FK).
💻 Usage Instructions

Add a New Flight: Follow the prompts to enter a flight number. You can select an existing destination from the list or add a new one instantly.

Filter Flights: Search for flights based on destination, status, or date.

Update Information: Select a flight by its ID to change its status, date, or destination. You can leave fields blank to keep current values.

Manage Destinations: View flight counts per city or delete unused destinations.

Summarised Reports: View high-level statistics on airline operations.
