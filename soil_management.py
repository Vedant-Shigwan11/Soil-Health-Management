import mysql.connector
import streamlit as st
import random
from faker import Faker
from datetime import datetime, timedelta
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

# Initialize Streamlit state for messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to add a message
def add_message(message, msg_type="success"):
    st.session_state['messages'] = [(msg_type, message)]  # Keep only the last message

# Database Connection Function
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        add_message(f"Error connecting to database: {e}", "error")
        return None

# Function to Insert Manual Soil Record
def insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        if not farm_location:
            add_message("Farm Location field must be filled!", "warning")
            return
        try:
            cursor.execute("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture))
            conn.commit()
            add_message("Soil record inserted successfully!", "success")
        except mysql.connector.Error as e:
            add_message(f"Error inserting record: {e}", "error")
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
def insert_bulk_records(total_records, batch_size):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        for _ in range(0, total_records, batch_size):
            data_batch = [generate_soil_data() for _ in range(batch_size)]
            cursor.executemany("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data_batch)
            conn.commit()
        add_message(f"{total_records} records inserted successfully!", "success")
        conn.close()
        st.rerun()

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
        df = pd.DataFrame(rows, columns=["Record No", "Farm Location", "Test Date", "Nitrogen Level", "Phosphorus Level", "Potassium Level", "pH Level", "Moisture Content"])
        st.dataframe(df, height=564, use_container_width=True)

# Streamlit GUI Setup
st.set_page_config(layout="wide")
st.title("🌱 Soil Management System")

conn = connect_db()
if conn:
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soil_health (
                record_no INT AUTO_INCREMENT PRIMARY KEY,
                farm_location VARCHAR(255) NOT NULL,
                test_date DATE,
                nitrogen_level FLOAT,
                phosphorus_level FLOAT,
                potassium_level FLOAT,
                pH_level FLOAT,
                moisture_content FLOAT
            );
        """)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# Create two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📝 Input Data")
    farm_location = st.text_input("Farm Location")
    test_date = st.date_input("Test Date")
    nitrogen = st.number_input("Nitrogen Level (mg/kg)", format="%.4f")
    phosphorus = st.number_input("Phosphorus Level (mg/kg)", format="%.4f")
    potassium = st.number_input("Potassium Level (mg/kg)", format="%.4f")
    pH = st.number_input("pH Level", format="%.4f")
    moisture = st.number_input("Moisture Content (%)", format="%.4f")
    
    if st.button("Insert Record"):
        insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture)
    
    st.subheader("📢 Messages")
    if st.session_state['messages']:
        msg_type, msg = st.session_state['messages'][0]
        if msg_type == "success":
            st.success(msg)
        elif msg_type == "error":
            st.error(msg)
        elif msg_type == "warning":
            st.warning(msg)
        else:
            st.info(msg)

with col2:
    st.header("📊 Last Records")
    limit = st.selectbox("Select Limit for Table", [10, 50, 100, 200, 500], index=2)
    bulk_quantity = st.selectbox("Select Bulk Quantity", [10, 50, 100, 500, 1000, 10000])
    
    if st.button("Insert Bulk Records"):
        batch_size = min(bulk_quantity, 10000)
        insert_bulk_records(bulk_quantity, batch_size)
    
    display_records(limit=limit)
