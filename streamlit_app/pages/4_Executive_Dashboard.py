import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import database as db

st.set_page_config(page_title="Executive Dashboard", page_icon="📈", layout="wide")
st.title("📈 Executive Production Dashboard")
st.markdown("Real-time visibility into order volumes, production bottlenecks, and factory throughput.")

try:
    # Query current state from the raw_production_logs (Simulating the BI tool querying the raw DB or Marts)
    # Ideally, a real BI tool queries `fct_order_fulfillment` in the Data Warehouse.
    # Since dbt runs in batch and we want real-time here, we query the operational DB:
    query = """
    SELECT 
        order_form_no,
        buyer_name,
        total_order_quantity AS total_qty_line_item,
        current_production_stage AS stage,
        is_delayed,
        is_shipped
    FROM analytics_marts.fct_order_fulfillment
    """
    df_live = db.fetch_data(query)
except Exception as e:
    st.error(f"Cannot load data: {e}")
    df_live = pd.DataFrame()

if not df_live.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    total_orders = df_live['order_form_no'].nunique()
    total_jeans = df_live['total_qty_line_item'].sum()
    completed = len(df_live[df_live['is_shipped'] == True])
    delayed = len(df_live[df_live['is_delayed'] == True])
    
    col1.metric("Total Active/Completed Orders", f"{total_orders:,}")
    col2.metric("Total Jeans in Pipeline", f"{int(total_jeans):,}")
    col3.metric("Shipped Orders", f"{completed:,}")
    col4.metric("Delayed Orders 🔴", f"{delayed:,}")

    st.markdown("---")
    
    st.markdown("### Production Bottleneck Analysis")
    stage_counts = df_live['stage'].value_counts().reset_index()
    stage_counts.columns = ['Stage', 'Order Count']
    
    # Define order of stages
    stages_order = ['Order Received', 'Cutting', 'Stitching', 'Washing', 'Ironing', 'Packaging Complete']
    stage_counts['Stage'] = pd.Categorical(stage_counts['Stage'], categories=stages_order, ordered=True)
    stage_counts = stage_counts.sort_values('Stage')
    
    fig = px.funnel(stage_counts, x='Order Count', y='Stage', title="Factory Pipeline Funnel", color_discrete_sequence=['#4C78A8'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Cloud Architecture Flow")
    st.info("💡 **Demo Context:** The data we just saw is flowing from the **Order Intake Form** directly into **PostgreSQL**. A background Airflow DAG uses **dbt** to generate analytical models like `fct_order_fulfillment` for this exact BI view!")
else:
    st.warning("No production data available. Please submit an order using the Order Intake form to populate the dashboard!")
