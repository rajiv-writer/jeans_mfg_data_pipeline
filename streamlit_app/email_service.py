import streamlit as st

def send_status_email(order_no, new_stage, buyer_name="Client"):
    """
    Simulates sending an email to the client and head office upon status update.
    """
    print(f"[EMAIL SERVICE MOCK] Sending email to {buyer_name} and Head Office...")
    print(f"Subject: Order #{order_no} Status Update: {new_stage}")
    
    if new_stage == "Packaging Complete":
        st.toast(f"📧 SUCCESS: Automated Email sent to {buyer_name} - 'Order is packaged and awaiting transport!'", icon="✉️")
    else:
        st.toast(f"📧 Notification sent to Head Office: Order #{order_no} moved to {new_stage}.", icon="ℹ️")
