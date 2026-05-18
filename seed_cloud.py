import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_generator'))
from simulate_quarterly_run import generate_data
import psycopg2
import psycopg2.extras

print("Generating simulated data for Cloud DB...")
order_data, prod_data, ship_data = generate_data()

print("Connecting to Neon DB...")
conn = psycopg2.connect("postgresql://neondb_owner:npg_Qf9WicMD4SxP@ep-green-frog-alo9hq5t-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require")
conn.autocommit = True
cursor = conn.cursor()

print("Clearing old data on cloud...")
cursor.execute("TRUNCATE TABLE raw_orders, raw_production_logs, raw_shipping_logs RESTART IDENTITY CASCADE;")

print(f"Loading {len(order_data)} orders...")
psycopg2.extras.execute_values(
    cursor,
    """INSERT INTO raw_orders (
        order_form_no, order_date, buyer_name, buyer_location, s_no, style_number,
        size_18_qty, size_20_qty, size_22_qty, size_24_qty, size_26_qty, size_28_qty, size_30_qty, size_32_qty, size_34_qty, size_36_qty, size_38_qty, size_40_qty, size_42_qty,
        unit_price, line_item_total, total_qty_line_item, ingested_at
    ) VALUES %s""",
    order_data
)

print(f"Loading {len(prod_data)} production logs...")
psycopg2.extras.execute_values(
    cursor,
    """INSERT INTO raw_production_logs (order_form_no, stage, updated_at, updated_by) VALUES %s""",
    prod_data
)

print(f"Loading {len(ship_data)} shipping logs...")
psycopg2.extras.execute_values(
    cursor,
    """INSERT INTO raw_shipping_logs (order_form_no, courier, tracking_number, shipped_at, status) VALUES %s""",
    ship_data
)

cursor.close()
conn.close()
print("Simulation data generation to Cloud complete!")
