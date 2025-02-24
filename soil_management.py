import streamlit as st
import google.generativeai as genai
import mysql.connector

# Configure Gemini API
API_KEY = "AIzaSyBKTbZgzd2e4ZmNykuQRGdrSc4h7YmhY9g"
genai.configure(api_key=API_KEY)

# Configure MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="vedant",
    database="soil_management"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS soil_recommendations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        soil_type VARCHAR(50),
        nitrogen INT,
        phosphorus INT,
        potassium INT,
        ph FLOAT,
        moisture INT,
        recommendation TEXT
    )
""")
conn.commit()

def get_crop_recommendation(soil_type, nitrogen, phosphorus, potassium, ph, moisture):
    model = genai.GenerativeModel("gemini-pro")  # Specify the model
    prompt = (f"<span style='color:black;'>Based on the following soil characteristics, recommend the best crops:</span> \n"
              f"<span style='color:black;'>Soil Type:</span> {soil_type}\n"
              f"<span style='color:black;'>Nitrogen:</span> {nitrogen}\n"
              f"<span style='color:black;'>Phosphorus:</span> {phosphorus}\n"
              f"<span style='color:black;'>Potassium:</span> {potassium}\n"
              f"<span style='color:black;'>PH:</span> {ph}\n"
              f"<span style='color:black;'>Moisture:</span> {moisture}%\n")
    
    response = model.generate_content(prompt)
    return response.text if response else "Could not generate a recommendation."

def insert_into_db(soil_type, nitrogen, phosphorus, potassium, ph, moisture, recommendation):
    cursor.execute("""
        INSERT INTO soil_recommendations (soil_type, nitrogen, phosphorus, potassium, ph, moisture, recommendation)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (soil_type, nitrogen, phosphorus, potassium, ph, moisture, recommendation))
    conn.commit()

# Streamlit UI customization
st.set_page_config(page_title="Soil Management System", page_icon="🌱", layout="centered")
st.markdown("<h1 style='text-align: center; color: black;'>Soil Management System 🌿</h1>", unsafe_allow_html=True)

st.markdown("""
    <style>
        .stApp {
            background-color: #DDEB9D;
            color: black;
        }
        .stButton > button {
            background-color: #27667B;
            color: white;
            font-size: 16px;
            border-radius: 10px;
            padding: 10px;
        }
        .recommendation-box {
            background-color: #A0C878;
            color: black;
            border: 3px solid #2E8B57;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            font-weight: bold;
            text-align: center;
        }
        input, select, textarea {
            background-color: #333 !important;
            color: white !important;
        }
        label {
            color: black !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Input fields
soil_type = st.selectbox("Select Soil Type:", ["Sandy", "Clayey", "Loamy", "Silty", "Peaty"])
nitrogen = st.number_input("Nitrogen Content (mg/kg)", min_value=0, max_value=500, step=1)
phosphorus = st.number_input("Phosphorus Content (mg/kg)", min_value=0, max_value=500, step=1)
potassium = st.number_input("Potassium Content (mg/kg)", min_value=0, max_value=500, step=1)
ph = st.number_input("Soil pH Level", min_value=0.0, max_value=14.0, step=0.1)
moisture = st.slider("Moisture Content (%)", 0, 100, 50)

if st.button("Get Crop Recommendation"):
    recommendation = get_crop_recommendation(soil_type, nitrogen, phosphorus, potassium, ph, moisture)
    insert_into_db(soil_type, nitrogen, phosphorus, potassium, ph, moisture, recommendation)
    st.markdown(f"<div class='recommendation-box'>{recommendation}</div>", unsafe_allow_html=True)
