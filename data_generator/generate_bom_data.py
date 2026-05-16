# C:\Data Engineering\jeans_mfg_data_pipeline\data_generator\generate_bom_data.py

import pandas as pd
import random
import os

STYLES = [
    f"{gender}-{fit}-{wash}"
    for gender in ["M", "W"]
    for fit in ["SKINNY", "SLIM", "REGULAR", "RELAXED"]
    for wash in ["LIGHT", "MEDIUM", "DARK", "BLACK"]
]

SIZES = [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42]

def generate_bom():
    data = []
    
    materials = [
        {"type": "Denim Fabric", "uom": "meters", "base_qty": 1.2},
        {"type": "Pocketing Fabric", "uom": "meters", "base_qty": 0.3},
        {"type": "Thread", "uom": "meters", "base_qty": 150},
        {"type": "Button", "uom": "pieces", "base_qty": 1},
        {"type": "Zipper", "uom": "pieces", "base_qty": 1},
        {"type": "Rivets", "uom": "pieces", "base_qty": 6},
        {"type": "Label", "uom": "pieces", "base_qty": 2},
    ]
    
    for style in STYLES:
        for size in SIZES:
            # Size scaling factor (Size 30 is baseline 1.0)
            size_factor = 1.0 + ((size - 30) * 0.03) 
            
            for mat in materials:
                # Thread and fabric scale with size. Buttons/zippers are constant.
                if mat['uom'] == 'meters':
                    qty = round(mat['base_qty'] * size_factor, 2)
                else:
                    qty = mat['base_qty']
                
                # Men's jeans might require slightly more fabric
                if style.startswith("M-") and mat['uom'] == 'meters':
                    qty = round(qty * 1.05, 2)
                    
                data.append({
                    'style_number': style,
                    'size': size,
                    'material_type': mat['type'],
                    'material_qty_per_unit': qty,
                    'unit_of_measure': mat['uom']
                })
                
    return pd.DataFrame(data)

if __name__ == '__main__':
    print("Generating BOM data...")
    df = generate_bom()
    
    script_dir = os.path.dirname(__file__)
    output_dir = os.path.join(script_dir, '..', 'raw_data_landing_zone')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'bom_sample.csv')
    df.to_csv(output_path, index=False)
    print(f"BOM data ({len(df)} rows) generated and saved to {output_path}")
