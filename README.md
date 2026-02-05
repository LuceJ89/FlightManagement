# FlightManagement

Airline Flight Management System
This repository contains a relational database solution and a Python-based Command-Line Interface (CLI) designed to manage airline logistics, including flights, pilots, and destinations.

Project Structure:
schema.sql: The Data Definition Language (DDL) script that establishes the relational schema, including Primary Keys and Foreign Key constraints.

db_manager.py: A management script used to initialise the SQLite database and seed it with 30+ sample records (10–15 per table) for testing purposes.

main.py: The primary application file featuring a CLI menu for staff interaction, including CRUD operations and data summarisation.

airline_data.db: The SQLite database file (generated after running the setup script).

Installation & Setup:
To run this project in GitHub Codespaces or a local environment, follow these steps:

Clone the Repository:

Bash
git clone <your-repo-link>
cd <repo-name>
Initialize the Database: Run the management script to create the tables and populate the sample data.

Bash
python db_manager.py
Launch the Application: Start the CLI menu to interact with the system.

Bash
python main.py
Features & Functionality:
The application supports the following core interactions required by the project brief:

Flight Management: Add new flights and update existing schedules or statuses.

Relational Filtering: Retrieve flights based on destination, status, or departure date using SQL JOIN logic.

Pilot Logistics: Assign pilots to flights and retrieve individual pilot schedules.

Destination Management: Create, update, or delete destination records with dependency checks.

Data Insights: Generate summarized reports showing flight counts per destination and per pilot using GROUP BY aggregations.

Database Design:
The system utilizes a normalized relational model based on the Chen Notation ER Diagram.

Entities: Pilots, Destinations, and Flights.

Integrity: Parameterised SQL queries are used throughout to prevent SQL injection and ensure data security.

Relationships: One-to-Many relationships are maintained via Foreign Keys in the Flights table.