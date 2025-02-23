import mysql.connector
import streamlit as st
from datetime import datetime
import pandas as pd

# MySQL Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vedant",
    "database": "soil_management"
}

# Streamlit Page Configurations
st.set_page_config(page_title="🌱 Soil Health Management", layout="wide")

# Database Connection Function
def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

# Insert Record Function
def insert_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, 
                potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture))
            conn.commit()
            st.success("✅ Record inserted successfully!")
        except mysql.connector.Error as e:
            st.error(f"❌ Insertion Error: {e}")
        finally:
            conn.close()

# Display Records Function
def fetch_records(limit=None):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM soil_health ORDER BY record_no DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=["Record No", "Farm Location", "Test Date", "Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture"])
            return df
        except mysql.connector.Error as e:
            st.error(f"❌ Fetch Error: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

# Streamlit UI
tab1, tab2 = st.tabs(["➕ Add Record", "📊 View Records"])

# Insert Record Section
with tab1:
    st.subheader("📝 Enter Soil Data")
    farm_location = st.text_input("🏡 Farm Location")
    test_date = st.date_input("📅 Test Date", datetime.today())
    nitrogen = st.number_input("🌱 Nitrogen (mg/kg)", min_value=0.0, format="%.2f")
    phosphorus = st.number_input("🔬 Phosphorus (mg/kg)", min_value=0.0, format="%.2f")
    potassium = st.number_input("🧪 Potassium (mg/kg)", min_value=0.0, format="%.2f")
    pH = st.number_input("⚖ pH Level", min_value=0.0, max_value=14.0, format="%.2f")
    moisture = st.number_input("💧 Moisture Content (%)", min_value=0.0, max_value=100.0, format="%.2f")
    
    if st.button("🚀 Insert Record"):
        if farm_location:
            insert_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture)
        else:
            st.warning("⚠ Please enter the farm location.")

# Display Records Section
with tab2:
    st.subheader("📊 Soil Health Records")
    limit = st.selectbox("🔍 Show last N records", [10, 50, 100, 200, "All"], index=2)
    records = fetch_records(None if limit == "All" else limit)
    st.dataframe(records, use_container_width=True)
