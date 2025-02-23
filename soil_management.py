import mysql.connector
import streamlit as st
import random
from faker import Faker
from datetime import datetime
import pandas as pd

# Initialize Faker
fake = Faker()

# MySQL Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vedant",
    "database": "soil_management"
}

# Streamlit Configurations
st.set_page_config(page_title="🌱 Soil Health Management", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #f0f8ff;
        }
        .stButton>button {
            background-color: #28a745;
            color: white;
            font-size: 16px;
            border-radius: 10px;
        }
        .stSelectbox, .stTextInput, .stNumberInput, .stDateInput {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Stylish Heading
st.markdown("""
    <h1 style='text-align: center; color: #2E8B57;'>🌿 Soil Health Management System 🌍</h1>
    <h3 style='text-align: center; color: #4682B4;'>Monitor & Improve Soil Quality for Better Yield 🚜</h3>
    <hr style='border: 2px solid #2E8B57;'>
""", unsafe_allow_html=True)

# Database Connection Function
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        st.error(f"❌ Error connecting to database: {e}")
        return None

# Insert Manual Record
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
            st.success("✅ Soil record inserted successfully!")
        except mysql.connector.Error as e:
            st.error(f"❌ Error inserting record: {e}")
        finally:
            conn.close()

# Display Records
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
        st.dataframe(df, use_container_width=True)

# Input Fields
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("📝 Enter Soil Data")
    farm_location = st.text_input("🏡 Farm Location")
    test_date = st.date_input("📅 Test Date", datetime.today())
    nitrogen = st.number_input("🌱 Nitrogen Level (mg/kg)", format="%.2f")
    phosphorus = st.number_input("🔬 Phosphorus Level (mg/kg)", format="%.2f")
    potassium = st.number_input("🧪 Potassium Level (mg/kg)", format="%.2f")
    pH = st.number_input("⚖ pH Level", format="%.2f")
    moisture = st.number_input("💧 Moisture Content (%)", format="%.2f")
    
    if st.button("🚀 Insert Record"):
        insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture)

# Display Records
with col2:
    st.subheader("📊 Soil Health Records")
    limit = st.selectbox("🔍 Show last N records", [10, 50, 100, 200, "All"], index=2)
    display_records(limit if isinstance(limit, int) else None)
