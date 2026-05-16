# pyrefly: ignore [missing-import]
import streamlit as st
import database as db

st.set_page_config(
    page_title="Jeans Manufacturing Portal",
    page_icon="👖",
    layout="wide"
)

st.title("👖 Welcome to the Jeans Manufacturing Portal")
st.markdown("""
This is the end-to-end prototype for our digital transformation initiative! 
Use the sidebar on the left to navigate between different operational views:

*   **1. Order Intake:** For sales reps or clients to place new bulk orders.
*   **2. Factory Floor:** For shop-floor managers to track and advance orders through production stages.
*   **3. Client Portal:** For clients to track their specific order status using their Order ID.
*   **4. Exec Dashboard:** For the owner to view high-level KPIs and production bottlenecks.
""")

# Initialize DB tables
try:
    db.init_db()
    st.success("Database connection established and operational schemas verified!")
except Exception as e:
    st.error(f"Could not connect to the database. Is Docker Desktop fully running? Error: {e}")
