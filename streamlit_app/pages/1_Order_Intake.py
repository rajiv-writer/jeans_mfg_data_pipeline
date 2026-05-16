import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import database as db
import random

st.set_page_config(page_title="Order Intake", page_icon="📝")
st.title("📝 New Order Intake Form")

with st.form("order_intake"):
    col1, col2 = st.columns(2)
    with col1:
        buyer_name = st.text_input("Buyer / Company Name")
        location = st.text_input("Delivery Location / City")
    with col2:
        style = st.selectbox("Style Code", ["M-SLIM-DARK", "M-RELAXED-LIGHT", "M-STRAIGHT-CLASSIC", "M-BOOTCUT-FADED", "M-TAPERED-WASH"])
        unit_price = st.number_input("Unit Price (₹)", min_value=100, value=800)
        
    st.subheader("Quantities by Size")
    cols = st.columns(6)
    sizes = [28, 30, 32, 34, 36, 38]
    qty_inputs = {}
    for i, size in enumerate(sizes):
        with cols[i % 6]:
            qty_inputs[f"size_{size}_qty"] = st.number_input(f"Size {size}", min_value=0, value=0, step=10)
            
    submitted = st.form_submit_button("Submit Order to Factory")

if submitted:
    if not buyer_name:
        st.error("Please enter a buyer name.")
    else:
        # Generate a new Order ID
        new_order_id = random.randint(200000, 299999)
        
        # Calculate total
        total_qty = sum(qty_inputs.values())
        line_item_total = total_qty * unit_price
        
        if total_qty == 0:
            st.warning("Please enter at least some quantity.")
        else:
            # Construct row for raw_orders
            import datetime
            now_str = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            
            # fill dummy variables for sizes 18-42
            all_sizes = {f'size_{s}_qty': 0 for s in [18,20,22,24,26,28,30,32,34,36,38,40,42]}
            all_sizes.update(qty_inputs)
            
            # Format columns
            columns = ['order_form_no', 'order_date', 'buyer_name', 'buyer_location', 's_no', 'style_number'] + list(all_sizes.keys()) + ['unit_price', 'line_item_total', 'total_qty_line_item', 'ingested_at']
            
            # Map values
            vals = [new_order_id, now_str, buyer_name, location, 1, style] + list(all_sizes.values()) + [unit_price, line_item_total, total_qty, datetime.datetime.utcnow()]
            
            # Generate Placeholders
            placeholders = ', '.join(['%s'] * len(vals))
            cols_str = ', '.join(columns)
            
            query = f"INSERT INTO raw_orders ({cols_str}) VALUES ({placeholders})"
            try:
                db.execute_query(query, tuple(vals))
                
                # Automatically log it in 'Order Received' stage
                db.execute_query(
                    "INSERT INTO raw_production_logs (order_form_no, stage, updated_by) VALUES (%s, %s, %s)",
                    (new_order_id, 'Order Received', 'System')
                )
                
                st.success(f"Order #{new_order_id} successfully dispatched to the factory floor!")
                st.balloons()
            except Exception as e:
                st.error(f"Database error: {e}")
