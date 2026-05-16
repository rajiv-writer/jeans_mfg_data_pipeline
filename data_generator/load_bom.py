import pandas as pd
import psycopg2
import psycopg2.extras
import os

df = pd.read_csv('raw_data_landing_zone/bom_sample.csv')

conn = psycopg2.connect(
    host="localhost",
    port="5433",
    dbname="jeans_source_db",
    user="user",
    password="password"
)
conn.autocommit = True
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS raw_bill_of_materials (
        style_number VARCHAR(100),
        size INT,
        material_type VARCHAR(100),
        material_qty_per_unit NUMERIC,
        unit_of_measure VARCHAR(50)
    )
''')
cursor.execute("TRUNCATE TABLE raw_bill_of_materials")

data = [tuple(x) for x in df.to_numpy()]
psycopg2.extras.execute_values(
    cursor,
    "INSERT INTO raw_bill_of_materials (style_number, size, material_type, material_qty_per_unit, unit_of_measure) VALUES %s",
    data
)

cursor.close()
conn.close()
print("Loaded BOM data")
