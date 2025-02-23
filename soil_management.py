import mysql.connector
import random
from faker import Faker
from datetime import datetime
import pandas as pd

# Initialize Faker for generating random data
fake = Faker()

# MySQL Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vedant",
    "database": "soil_management"
}

# Database Connection Function
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to Insert Manual Soil Record
def insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture))
            conn.commit()
            print("Soil record inserted successfully!")
        except mysql.connector.Error as e:
            print(f"Error inserting record: {e}")
        finally:
            conn.close()

# Function to Generate Random Data for Bulk Insert
def generate_soil_data():
    return (
        fake.city(),
        fake.date_between(start_date="-2y", end_date="today"),
        round(random.uniform(0.1, 5.0), 2),
        round(random.uniform(0.1, 5.0), 2),
        round(random.uniform(0.1, 5.0), 2),
        round(random.uniform(4.5, 8.5), 2),
        round(random.uniform(5.0, 50.0), 2)
    )

# Function to Insert Bulk Records
def insert_bulk_records(total_records, batch_size=1000):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        for _ in range(0, total_records, batch_size):
            data_batch = [generate_soil_data() for _ in range(min(batch_size, total_records))]
            cursor.executemany("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data_batch)
            conn.commit()
        print(f"{total_records} records inserted successfully!")
        conn.close()

# Function to Display Records
def display_records(limit=None):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "SELECT * FROM soil_health ORDER BY record_no DESC"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(rows, columns=["Record No", "Farm Location", "Test Date", "Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture"])
        print(df)

if __name__ == "__main__":
    while True:
        print("\nSoil Management System")
        print("1. Insert Manual Record")
        print("2. Insert Bulk Records")
        print("3. Display Records")
        print("4. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            farm_location = input("Enter Farm Location: ")
            test_date = input("Enter Test Date (YYYY-MM-DD): ")
            nitrogen = float(input("Enter Nitrogen Level (mg/kg): "))
            phosphorus = float(input("Enter Phosphorus Level (mg/kg): "))
            potassium = float(input("Enter Potassium Level (mg/kg): "))
            pH = float(input("Enter pH Level: "))
            moisture = float(input("Enter Moisture Content (%): "))
            insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture)
        
        elif choice == "2":
            total_records = int(input("Enter the number of records to insert: "))
            insert_bulk_records(total_records)
        
        elif choice == "3":
            limit = input("Enter the number of records to display (or press Enter for all): ")
            limit = int(limit) if limit.isdigit() else None
            display_records(limit)
        
        elif choice == "4":
            print("Exiting...\n")
            break
        else:
            print("Invalid choice. Please try again.")
