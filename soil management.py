import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
import random
from faker import Faker
from datetime import datetime

# Initialize Faker for generating random data
fake = Faker()

# MySQL Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vedant",
    "database": "soil_management",
    "auth_plugin": "mysql_native_password"
}

# Function to connect to the database
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

# Function to check if the table exists, and create it if missing
def initialize_db():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS soil_management")
        cursor.execute("USE soil_management")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soil_health (
                record_no INT AUTO_INCREMENT PRIMARY KEY,
                farm_location VARCHAR(255) NOT NULL,
                test_date DATE NOT NULL,
                nitrogen_level FLOAT NOT NULL,
                phosphorus_level FLOAT NOT NULL,
                potassium_level FLOAT NOT NULL,
                pH_level FLOAT NOT NULL CHECK (pH_level BETWEEN 4.5 AND 8.5),
                moisture_content FLOAT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

# Function to validate date format
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Function to insert a manual record
def insert_manual_record():
    farm_location = entry_farm_location.get()
    test_date = entry_test_date.get()

    if not farm_location or not validate_date(test_date):
        messagebox.showerror("Input Error", "Farm Location cannot be empty and Date must be in YYYY-MM-DD format.")
        return

    try:
        nitrogen = float(entry_nitrogen.get())
        phosphorus = float(entry_phosphorus.get())
        potassium = float(entry_potassium.get())
        pH = float(entry_pH.get())
        moisture = float(entry_moisture.get())

        if not (4.5 <= pH <= 8.5):
            messagebox.showwarning("Validation Error", "pH level should be between 4.5 and 8.5.")
            return
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture))
            conn.commit()
            messagebox.showinfo("Success", "Soil record inserted successfully!")
            fetch_records()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error inserting record: {e}")
        finally:
            conn.close()

# Function to generate random soil data
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

# Function to insert bulk records
def insert_bulk_records():
    try:
        bulk_quantity = int(bulk_quantity_var.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please select a valid bulk quantity.")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            data_batch = [generate_soil_data() for _ in range(bulk_quantity)]
            cursor.executemany("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data_batch)
            conn.commit()
            messagebox.showinfo("Success", f"{bulk_quantity} records inserted successfully!")
            fetch_records()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error inserting bulk records: {e}")
        finally:
            conn.close()

# Function to fetch and display records
def fetch_records():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soil_health ORDER BY record_no DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", tk.END, values=row)

# Initialize Database
initialize_db()

# GUI Setup
root = tk.Tk()
root.title("Soil Management System")
root.geometry("900x600")

# Input Frame
input_frame = ttk.LabelFrame(root, text="Input Data")
input_frame.pack(fill="x", padx=10, pady=5)

fields = ["Farm Location", "Test Date (YYYY-MM-DD)", "Nitrogen Level", "Phosphorus Level", "Potassium Level", "pH Level", "Moisture Content"]
entries = []
for i, field in enumerate(fields):
    label = ttk.Label(input_frame, text=field)
    label.grid(row=i, column=0, padx=5, pady=2, sticky="w")
    entry = ttk.Entry(input_frame)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

entry_farm_location, entry_test_date, entry_nitrogen, entry_phosphorus, entry_potassium, entry_pH, entry_moisture = entries
entry_test_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

insert_btn = ttk.Button(input_frame, text="Insert Record", command=insert_manual_record)
insert_btn.grid(row=7, column=0, columnspan=2, pady=10)

# Bulk Insert Section
bulk_frame = ttk.LabelFrame(root, text="Bulk Insert")
bulk_frame.pack(fill="x", padx=10, pady=5)

bulk_quantity_var = tk.StringVar(value="10")
bulk_dropdown = ttk.Combobox(bulk_frame, textvariable=bulk_quantity_var, values=[10, 50, 100, 500, 1000, 10000])
bulk_dropdown.pack(side="left", padx=5)
bulk_btn = ttk.Button(bulk_frame, text="Insert Bulk Records", command=insert_bulk_records)
bulk_btn.pack(side="left", padx=5)

# Display Table
tree = ttk.Treeview(root, columns=("Record No", "Farm Location", "Test Date", "Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture"), show="headings")
tree.pack(fill="both", expand=True)
fetch_records()

root.mainloop()
