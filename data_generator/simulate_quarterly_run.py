import random
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

# Constants
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 3, 31)
NUM_ORDERS = 500

BUYERS = [
    {"name": "Reliance Trends", "location": "Mumbai"},
    {"name": "Shoppers Stop", "location": "Delhi"},
    {"name": "Lifestyle", "location": "Bangalore"},
    {"name": "Local Boutique A", "location": "Pune"}
]

STYLES = [f"{gender}-{fit}-{wash}" for gender in ["M", "W"] for fit in ["SKINNY", "SLIM"] for wash in ["LIGHT", "DARK"]]
STAGES = ["Cutting", "Stitching", "Washing", "Packing"]

def generate_data():
    order_data = []
    prod_data = []
    ship_data = []
    order_dates = {}
    current_order_id = 200000
    
    days_range = (END_DATE - START_DATE).days
    
    # GENERATE ORDERS
    for i in range(NUM_ORDERS):
        random_days = random.randint(0, days_range)
        order_date = START_DATE + timedelta(days=random_days)
        order_dates[current_order_id] = order_date
        
        buyer = random.choice(BUYERS)
        num_line_items = random.randint(1, 3)
        
        for s_no in range(1, num_line_items + 1):
            style = random.choice(STYLES)
            qty = random.randint(50, 300)
            unit_price = round(random.uniform(600, 1000), 2)
            
            row = [
                current_order_id,
                order_date.strftime('%Y-%m-%d'),
                buyer['name'],
                buyer['location'],
                s_no,
                style,
                0,0,0,0,0,0,0,qty,0,0,0,0,0, # size_18 to size_42, 32 is qty
                unit_price,
                round(qty * unit_price, 2),
                qty,
                datetime.utcnow() # ingested_at
            ]
            order_data.append(row)
        current_order_id += 1

    # GENERATE LOGS
    order_ids = list(order_dates.keys())
    random.shuffle(order_ids)
    
    happy_path = order_ids[:int(0.6 * len(order_ids))]
    stuck_prod = order_ids[int(0.6 * len(order_ids)):int(0.8 * len(order_ids))]
    lack_material = order_ids[int(0.8 * len(order_ids)):int(0.9 * len(order_ids))]
    anomalies = order_ids[int(0.9 * len(order_ids)):]
    
    def add_prod_log(oid, stage, days_after_order):
        update_time = order_dates[oid] + timedelta(days=days_after_order, hours=random.randint(8,18))
        if update_time > datetime.now():
            return update_time, False
        prod_data.append([oid, stage, update_time, 'Auto_Sim'])
        return update_time, True

    for oid in happy_path:
        days = random.randint(1, 3)
        for stage in STAGES:
            dt, valid = add_prod_log(oid, stage, days)
            days += random.randint(1, 3)
            if not valid: break
        
        if valid:
            ship_data.append([oid, 'BlueDart', f'TRK{oid}HP', dt + timedelta(days=1), 'Shipped'])
            
    for oid in stuck_prod:
        days = 1
        dt, valid = add_prod_log(oid, "Cutting", days)
        stuck_at = random.choice(["Stitching", "Washing"])
        if valid:
            days += random.randint(2, 5)
            dt, valid = add_prod_log(oid, stuck_at, days)
            
    for oid in lack_material:
        add_prod_log(oid, "Cutting", 2)

    for oid in anomalies:
        days = random.randint(1, 3)
        dt, valid = add_prod_log(oid, "Cutting", days)
        if valid:
            days += random.randint(1, 2)
            dt, valid = add_prod_log(oid, "Packing", days)
        if valid:
            ship_data.append([oid, 'FedEx', f'TRK{oid}AN', dt + timedelta(days=1), 'Shipped'])

    return order_data, prod_data, ship_data

if __name__ == "__main__":
    print("Generating simulated data...")
    order_data, prod_data, ship_data = generate_data()
    
    print("Connecting to DB...")
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        dbname="jeans_source_db",
        user="user",
        password="password"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Clearing old data...")
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
    print("Simulation data generation complete!")
