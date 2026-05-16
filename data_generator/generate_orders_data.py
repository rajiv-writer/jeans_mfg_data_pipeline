# C:\Data Engineering\jeans_mfg_data_pipeline\data_generator\generate_orders_data.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# --- Configurations ---
NUM_ORDERS = 5000 # 5000 orders, each with 1-8 line items -> ~20k-40k rows
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2023, 12, 31)

BUYERS = [
    {"name": "Reliance Trends", "location": "Mumbai", "volume_multiplier": 3.0},
    {"name": "Shoppers Stop", "location": "Delhi", "volume_multiplier": 2.5},
    {"name": "Lifestyle", "location": "Bangalore", "volume_multiplier": 2.0},
    {"name": "Max Fashion", "location": "Chennai", "volume_multiplier": 1.5},
    {"name": "Local Boutique A", "location": "Pune", "volume_multiplier": 0.5},
    {"name": "Local Boutique B", "location": "Hyderabad", "volume_multiplier": 0.3},
]

STYLES = [
    f"{gender}-{fit}-{wash}"
    for gender in ["M", "W"]
    for fit in ["SKINNY", "SLIM", "REGULAR", "RELAXED"]
    for wash in ["LIGHT", "MEDIUM", "DARK", "BLACK"]
]

SIZES = [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42]

def get_seasonal_weight(date):
    # Higher logic in Sep-Nov (Pre-winter/Festive India)
    month = date.month
    if month in [9, 10, 11]:
        return random.uniform(1.5, 2.5)
    elif month in [12, 1]:
        return random.uniform(0.8, 1.2)
    else:
        return random.uniform(0.5, 1.0)

def generate_size_distribution(total_qty, gender):
    # Adult male/female typically centers around 30-34
    # Kid's sizes (18-26) are rarer for this brand or distinct
    # Let's use a normal distribution centered at index of size 32 (idx 7)
    mean_idx = 7 if gender == "M" else 6
    std_dev = 2.0
    
    # Generate distribution
    probs = np.exp(-0.5 * ((np.arange(len(SIZES)) - mean_idx) / std_dev)**2)
    probs /= probs.sum() # Normalize
    
    # Assign quantities
    quantities = np.random.multinomial(total_qty, probs)
    return {f'size_{s}_qty': q for s, q in zip(SIZES, quantities)}

def generate_orders():
    data = []
    current_order_id = 100000
    
    # Generate random dates sorted
    days_range = (END_DATE - START_DATE).days
    
    for i in range(NUM_ORDERS):
        random_days = random.randint(0, days_range)
        order_date = START_DATE + timedelta(days=random_days)
        
        seasonal_weight = get_seasonal_weight(order_date)
        buyer = random.choices(BUYERS, weights=[b['volume_multiplier'] for b in BUYERS])[0]
        
        num_line_items = random.randint(1, 8)
        
        for s_no in range(1, num_line_items + 1):
            style = random.choice(STYLES)
            gender = style.split('-')[0]
            
            # Base price
            base_price = random.uniform(600, 1200)
            if "SKINNY" in style: base_price += 100
            if "BLACK" in style: base_price += 50
            unit_price = round(base_price, 2)
            
            # Base quantity modulated by buyer size and seasonality
            avg_qty = int(200 * buyer['volume_multiplier'] * seasonal_weight)
            total_qty_line_item = max(10, int(random.normalvariate(avg_qty, avg_qty * 0.2)))
            
            size_quantities = generate_size_distribution(total_qty_line_item, gender)
            line_item_total = round(total_qty_line_item * unit_price, 2)
            
            row = {
                'order_form_no': current_order_id,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'buyer_name': buyer['name'],
                'buyer_location': buyer['location'],
                's_no': s_no,
                'style_number': style,
            }
            row.update(size_quantities)
            row.update({
                'unit_price': unit_price,
                'line_item_total': line_item_total,
                'total_qty_line_item': total_qty_line_item
            })
            data.append(row)
            
        current_order_id += 1
        
    df = pd.DataFrame(data)
    df.sort_values('order_date', inplace=True)
    return df

if __name__ == '__main__':
    print("Generating historic orders...")
    df = generate_orders()
    
    script_dir = os.path.dirname(__file__)
    output_dir = os.path.join(script_dir, '..', 'raw_data_landing_zone')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'orders_sample.csv')
    df.to_csv(output_path, index=False)
    print(f"Sample data ({len(df)} rows) generated and saved to {output_path}")