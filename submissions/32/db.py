# create_db.py
import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = "my_data.db"

def setup_database():
    """
    Connects to the SQLite database, creates necessary tables, and
    populates them with 10 rows of sample data each.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Define a list of sample users for a potential 'users' table
    # (Included based on the user's original incomplete code structure)
    sample_users = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com")
    ]
    
    # 0. Create a basic users table (to resolve the executemany error)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            name TEXT NOT NULL, 
            email TEXT UNIQUE
        )
    ''')

    # 1. Create BP Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bp (
            value INTEGER,      -- beats per minute
            time DATETIME,      -- Measurement time
            patient_name TEXT   -- patient name
        )
    ''')
    
    # 2. Create GlucoseLevel Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GlucoseLevel (
            value REAL,         -- mg/dL
            time DATETIME,
            patient_name TEXT
        )
    ''')

    # 3. Create Fall Table (using "GPS" as a simplified location)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fall (
            gps TEXT,           -- Simplified GPS/Location data
            time DATETIME,
            patient_name TEXT
        )
    ''')
    
    # 4. Create LastEaten Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LastEaten (
            meal_name TEXT,     -- e.g., Breakfast, Lunch
            time DATETIME,
            patient_name TEXT
        )
    ''')
    
    # --- Insert Sample Data (10 points for each) ---
    patient_names = ["Alice", "Bob", "Charlie", "Diana"]
    # Start 10 hours ago and increment by one hour for each entry
    start_time = datetime.now() - timedelta(hours=10)

    for i in range(10):
        t = start_time + timedelta(hours=i)
        name = random.choice(patient_names)
        
        # BP Data: 60-100 BPM
        cursor.execute("INSERT INTO bp VALUES (?, ?, ?)", 
                       (random.randint(60, 100), t.isoformat(), name))

        # GlucoseLevel Data: 80-150 mg/dL
        cursor.execute("INSERT INTO GlucoseLevel VALUES (?, ?, ?)", 
                       (random.uniform(80.0, 150.0), t.isoformat(), name))

        # Fall Data: Sample GPS coordinates/locales
        locations = ["47.6062,-122.3321 (Seattle)", "34.0522,-118.2437 (LA)", "40.7128,-74.0060 (NYC)"]
        cursor.execute("INSERT INTO Fall VALUES (?, ?, ?)", 
                       (random.choice(locations), t.isoformat(), name))
        
        # LastEaten Data: Sample meals
        meals = ["Sandwich", "Salad", "Soup", "Fruit"]
        cursor.execute("INSERT INTO LastEaten VALUES (?, ?, ?)", 
                       (random.choice(meals), t.isoformat(), name))


    # Insert sample data into the 'users' table
    cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", sample_users)

    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' created and populated with sample data.")

if __name__ == '__main__':
    setup_database()