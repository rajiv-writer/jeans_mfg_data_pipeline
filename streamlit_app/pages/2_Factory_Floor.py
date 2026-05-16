import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import database as db
import email_service as es

st.set_page_config(page_title="Factory Floor", page_icon="🏭", layout="wide")
st.title("🏭 Factory Floor Production Tracker")

STAGES = ['Order Received', 'Cutting', 'Stitching', 'Washing', 'Ironing', 'Packaging Complete']

# Fetch all active orders
try:
    # We want the LATEST stage per order.
    query = """
    WITH RankedLogs AS (
        SELECT order_form_no, stage, updated_at,
               ROW_NUMBER() OVER(PARTITION BY order_form_no ORDER BY updated_at DESC) as rn
        FROM raw_production_logs
    )
    SELECT r.order_form_no, o.buyer_name, o.style_number, o.total_qty_line_item, r.stage as current_stage, r.updated_at,
           f.is_delayed, f.days_in_current_stage
    FROM RankedLogs r
    JOIN raw_orders o ON r.order_form_no = o.order_form_no
    LEFT JOIN analytics_marts.fct_order_fulfillment f ON r.order_form_no = f.order_form_no AND o.style_number = f.style_number
    WHERE r.rn = 1 AND r.stage != 'Packaging Complete'
    ORDER BY r.updated_at DESC
    LIMIT 50
    """
    active_orders = db.fetch_data(query)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    active_orders = pd.DataFrame()

if active_orders.empty:
    st.info("No active orders on the factory floor right now. Place an order in the Order Intake form to start!")
else:
    st.markdown("### Active Production Queue")
    
    for _, row in active_orders.iterrows():
        delayed_icon = "🔴 DELAYED " if row.get('is_delayed') else ""
        days_str = f"({row.get('days_in_current_stage')} days in stage) " if row.get('is_delayed') else ""
        with st.expander(f"{delayed_icon}Order #{row['order_form_no']} - {row['buyer_name']} ({row['total_qty_line_item']} units of {row['style_number']})"):
            st.markdown(f"**Current Stage:** `{row['current_stage']}` {days_str}(Updated: {row['updated_at'].strftime('%Y-%m-%d %H:%M')})")
            
            curr_idx = STAGES.index(row['current_stage']) if row['current_stage'] in STAGES else 0
            
            if curr_idx < len(STAGES) - 1:
                next_stage = STAGES[curr_idx + 1]
                if st.button(f"Advance to '{next_stage}'", key=f"btn_{row['order_form_no']}"):
                    db.execute_query(
                        "INSERT INTO raw_production_logs (order_form_no, stage, updated_by) VALUES (%s, %s, %s)",
                        (row['order_form_no'], next_stage, 'Floor Worker')
                    )
                    st.success(f"Order #{row['order_form_no']} advanced to {next_stage}! Refreshing...")
                    es.send_status_email(row['order_form_no'], next_stage, row['buyer_name'])
                    st.rerun()
            else:
                st.success("This order is fully packaged!")
                
st.markdown("---")
st.markdown("#### Log History")
if st.button("Refresh Logs"):
    st.table(db.fetch_data("SELECT * FROM raw_production_logs ORDER BY updated_at DESC LIMIT 10"))
