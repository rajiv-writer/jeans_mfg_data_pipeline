import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import database as db

st.set_page_config(page_title="Client Portal", page_icon="📦")
st.title("📦 Client Order Tracking Portal")

st.markdown("Enter your Order Tracking Number below to see its real-time production status.")

order_input = st.text_input("Order Number (e.g. 250012)")

if order_input:
    # Validate
    try:
        order_no = int(order_input)
        
        # Fetch status
        query = """
        SELECT r.stage, r.updated_at
        FROM raw_production_logs r
        WHERE r.order_form_no = %s
        ORDER BY r.updated_at DESC
        """
        logs = db.fetch_data(query, (order_no,))
        
        # Fetch shipping details
        dwh_query = """
        SELECT is_shipped, shipped_at, courier, tracking_number 
        FROM analytics_marts.fct_order_fulfillment 
        WHERE order_form_no = %s LIMIT 1
        """
        shipping_info = db.fetch_data(dwh_query, (order_no,))
        
        if logs.empty:
            st.warning("Order not found or hasn't entered production yet.")
        else:
            latest_stage = logs.iloc[0]['stage']
            
            is_shipped = False
            if not shipping_info.empty and shipping_info.iloc[0].get('is_shipped'):
                is_shipped = True
                latest_stage = 'Shipped'
            
            st.subheader(f"Status for Order #{order_no}: {latest_stage}")
            
            stages = ['Order Received', 'Cutting', 'Stitching', 'Washing', 'Packing', 'Shipped']
            current_idx = stages.index(latest_stage) if latest_stage in stages else 0
            
            progress = current_idx / (len(stages) - 1.0)
            st.progress(progress)
            
            if is_shipped:
                st.success(f"Your order has been SHIPPED via {shipping_info.iloc[0]['courier']}! Tracking Number: **{shipping_info.iloc[0]['tracking_number']}**")
            elif latest_stage == 'Packing':
                st.info("Your order is fully packaged and ready for transport!")
            
            st.markdown("### Detailed Production History")
            st.table(logs)
            
    except ValueError:
        st.error("Please enter a valid numeric Order Number.")
