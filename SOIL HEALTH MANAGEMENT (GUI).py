import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
import random
from faker import Faker
from datetime import datetime

# Initialize Faker
fake = Faker()

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vedant",
    "database": "soil_management",
    "auth_plugin": "mysql_native_password"
}

# Connect to MySQL Database
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

# Initialize the database and create table if not exists
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

# Validate Date Input
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Insert Manual Record
def insert_manual_record():
    farm_location = entry_farm_location.get()
    test_date = entry_test_date.get()

    if not farm_location or not validate_date(test_date):
        messagebox.showerror("Input Error", "⚠️ Farm Location cannot be empty and Date must be in YYYY-MM-DD format.")
        return

    try:
        nitrogen = float(entry_nitrogen.get())
        phosphorus = float(entry_phosphorus.get())
        potassium = float(entry_potassium.get())
        pH = float(entry_pH.get())
        moisture = float(entry_moisture.get())

        if not (4.5 <= pH <= 8.5):
            messagebox.showwarning("Validation Error", "⚠️ pH level should be between 4.5 and 8.5.")
            return
    except ValueError:
        messagebox.showerror("Input Error", "⚠️ Please enter valid numeric values.")
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
            messagebox.showinfo("✅ Success", "Soil record inserted successfully!")
            fetch_records()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"⚠️ Error inserting record: {e}")
        finally:
            conn.close()

# Fetch and Display Records
def fetch_records():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soil_health ORDER BY record_no DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        tree.delete(*tree.get_children())
        for i, row in enumerate(rows):
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            tree.insert("", tk.END, values=row, tags=(tag,))

# GUI Setup
root = tk.Tk()
root.title("🌱 Soil Health Management System")
root.geometry("1100x700")
root.configure(bg="#E6F7FF")  # Light Blue Background

# Title Box
title_frame = tk.Frame(root, bg="#005792", padx=20, pady=10)
title_frame.pack(pady=10, fill="x")
heading_label = tk.Label(title_frame, text="🌱 Soil Health Monitoring System 🌍", 
                         font=("Arial", 22, "bold"), fg="white", bg="#005792")
heading_label.pack(pady=5)

# Input Frame
input_frame = ttk.LabelFrame(root, text="📋 Enter Soil Data")
input_frame.pack(fill="x", padx=10, pady=5)

fields = [
    "📍 Farm Location", "📆 Test Date (YYYY-MM-DD)", "💧 Nitrogen Level",
    "🔥 Phosphorus Level", "🌿 Potassium Level", "🧪 pH Level", "🌡️ Moisture Content"
]
entries = []
for i, field in enumerate(fields):
    label = tk.Label(input_frame, text=f"• {field}:", font=("Arial", 12, "bold"), fg="#005792", bg="#E6F7FF")
    label.grid(row=i, column=0, padx=5, pady=2, sticky="w")
    entry = tk.Entry(input_frame, width=30)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

entry_farm_location, entry_test_date, entry_nitrogen, entry_phosphorus, entry_potassium, entry_pH, entry_moisture = entries
entry_test_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

# Insert Button
insert_btn = tk.Button(input_frame, text="➕ Insert Record", command=insert_manual_record, 
                       bg="#28A745", fg="white", font=("Arial", 12, "bold"))
insert_btn.grid(row=7, column=0, columnspan=2, pady=10)

# Bulk Insert Section
bulk_frame = ttk.LabelFrame(root, text="📦 Bulk Insert")
bulk_frame.pack(fill="x", padx=10, pady=5)
bulk_quantity_var = tk.StringVar(value="10")
bulk_dropdown = ttk.Combobox(bulk_frame, textvariable=bulk_quantity_var, values=[10, 50, 100, 500, 1000, 10000])
bulk_dropdown.pack(side="left", padx=5)
bulk_btn = tk.Button(bulk_frame, text="📊 Insert Bulk Records", command=lambda: messagebox.showinfo("⚠️ Coming Soon!", "Bulk insert is under maintenance."), 
                     bg="#FFC107", fg="black", font=("Arial", 12, "bold"))
bulk_btn.pack(side="left", padx=5)

# Table to Display Records
tree_frame = ttk.LabelFrame(root, text="📋 Last 100 Records")
tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
columns = ("Record No", "Farm Location", "Test Date", "Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
tree.tag_configure('oddrow', background='#D6EAF8', foreground='black')  # Soft Blue
tree.tag_configure('evenrow', background='#FDEBD0', foreground='black')  # Soft Orange
for col in columns:
    tree.heading(col, text=col, anchor="center")
    tree.column(col, width=140, anchor="center")
tree.pack(fill="both", expand=True)

# Load Records
fetch_records()

# Run App
root.mainloop()
