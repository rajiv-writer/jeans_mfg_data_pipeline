# C:\Users\Rajiv Nair\jeans_mfg_data_pipeline\data_generator\generate_orders_data.py

import pandas as pd
import random
from datetime import datetime, timedelta
import os

# --- Configuration ---
NUM_ORDERS = 100 # Generate 100 sample orders
NUM_LINE_ITEMS_PER_ORDER = [1, 5] # Each order has 1 to 5 line items
STYLE_NUMBERS = [f"STYLE-{i:03d}" for i in range(100, 150)] # Sample styles
SIZES = [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42]
BUYERS = ["Bindas Guntur", "Fashion Hub Delhi", "Trendy Threads Mumbai", "Elite Garments Chennai", "Silk Route Kolkata"]

# --- Data Generation Logic ---
data = []
current_order_id = 1000

for _ in range(NUM_ORDERS):
    order_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d') # Orders over last 6 months
    buyer_name = random.choice(BUYERS)
    buyer_location = buyer_name.split()[-1] # Simple extraction of city

    num_line_items = random.randint(*NUM_LINE_ITEMS_PER_ORDER)

    for s_no in range(1, num_line_items + 1):
        style_number = random.choice(STYLE_NUMBERS)
        unit_price = round(random.uniform(500, 1500), 2) # Random price per unit

        # Generate quantities for each size
        size_quantities = {}
        total_qty_line_item = 0
        for size in SIZES:
            qty = random.randint(0, 50) # Random quantity per size
            size_quantities[f'size_{size}_qty'] = qty
            total_qty_line_item += qty

        line_item_total = round(total_qty_line_item * unit_price, 2)

        row = {
            'order_form_no': current_order_id,
            'order_date': order_date,
            'buyer_name': buyer_name,
            'buyer_location': buyer_location,
            's_no': s_no,
            'style_number': style_number,
            **size_quantities, # Unpack size quantities into row
            'unit_price': unit_price,
            'line_item_total': line_item_total,
            'total_qty_line_item': total_qty_line_item # Added for clarity
        }
        data.append(row)
    current_order_id += 1

df = pd.DataFrame(data)

# --- Save to CSV ---
# Define the output directory relative to the script location
# This should be your raw_data_landing_zone folder at the project root
script_dir = os.path.dirname(__file__)
output_dir = os.path.join(script_dir, '..', 'raw_data_landing_zone') # Go up one level (from data_generator to jeans_mfg_data_pipeline), then into raw_data_landing_zone

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'orders_sample.csv')
df.to_csv(output_path, index=False)
print(f"Sample data generated and saved to {output_path}")