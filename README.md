# CSC370-Database-Project

## Green-not-Greed (GnG) Database Interface

This Python script provides an interactive interface for managing and querying the Green-not-Greed (GnG) database. Users can perform various operations such as executing predefined queries, setting up campaigns, reporting funds, browsing membership history, and much more.

### Features

- Execute predefined queries from the GnG database.
- Setup campaigns, schedule events, and add volunteers.
- Report funds, including donation history and expense breakdown.
- Browse membership history to track member participation.
- View ongoing campaigns and their events, as well as past campaigns.

### Requirements

- Python 3.x
- psycopg2 library
- PostgreSQL database with the GnG schema

### Installation

1. Clone the repository or download the Python script (`gng_database_interface.py`).
2. Install the required dependencies: ```pip install psycopg2```
3. Ensure you have access to a PostgreSQL database with the GnG schema.
4. Configure the database connection parameters (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) in the Python script according to your PostgreSQL setup.

## Usage

1. Run the Python script: ```python python gng.py```

2. Follow the on-screen menu prompts to perform various operations.
3. Interact with the database by selecting options from the menu.

### Known Issues

- Make sure you have a connection to a Database before running this

