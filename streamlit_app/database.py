import psycopg2
import pandas as pd
# pyrefly: ignore [missing-import]
import streamlit as st

# Use Streamlit Secrets if deployed, otherwise fallback to local Docker DB
@st.cache_resource
def get_connection():
    if "db_host" in st.secrets:
        # Running on Streamlit Cloud
        kwargs = {
            "host": st.secrets["db_host"],
            "port": st.secrets["db_port"],
            "dbname": st.secrets["db_name"],
            "user": st.secrets["db_user"],
            "password": st.secrets["db_password"]
        }
        if "sslmode" in st.secrets:
            kwargs["sslmode"] = st.secrets["sslmode"]
        conn = psycopg2.connect(**kwargs)
        conn.autocommit = True
        return conn
    else:
        # Running Locally
        conn = psycopg2.connect(
            host="localhost",
            port="5433",
            dbname="jeans_source_db",
            user="user",
            password="password"
        )
        conn.autocommit = True
        return conn


def init_db():
    # Initialize the required tables if they don't exist
    conn = get_connection()
    cur = conn.cursor()
    
    # 0. raw_orders
    cur.execute('''
        CREATE TABLE IF NOT EXISTS raw_orders (
            order_form_no INT,
            order_date DATE,
            buyer_name VARCHAR(255),
            buyer_location VARCHAR(255),
            s_no INT,
            style_number VARCHAR(100),
            size_18_qty INT DEFAULT 0,
            size_20_qty INT DEFAULT 0,
            size_22_qty INT DEFAULT 0,
            size_24_qty INT DEFAULT 0,
            size_26_qty INT DEFAULT 0,
            size_28_qty INT DEFAULT 0,
            size_30_qty INT DEFAULT 0,
            size_32_qty INT DEFAULT 0,
            size_34_qty INT DEFAULT 0,
            size_36_qty INT DEFAULT 0,
            size_38_qty INT DEFAULT 0,
            size_40_qty INT DEFAULT 0,
            size_42_qty INT DEFAULT 0,
            unit_price NUMERIC,
            line_item_total NUMERIC,
            total_qty_line_item INT,
            ingested_at TIMESTAMP
        )
    ''')
    
    # 1. raw_production_logs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS raw_production_logs (
            log_id SERIAL PRIMARY KEY,
            order_form_no INT NOT NULL,
            stage VARCHAR(50) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(50)
        )
    ''')
    
    # 2. raw_shipping_logs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS raw_shipping_logs (
            shipping_id SERIAL PRIMARY KEY,
            order_form_no INT NOT NULL,
            courier VARCHAR(100),
            tracking_number VARCHAR(100),
            shipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50)
        )
    ''')
    
    conn.commit()
    cur.close()

def execute_query(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()

def fetch_data(query, params=None):
    conn = get_connection()
    return pd.read_sql_query(query, conn, params=params)
