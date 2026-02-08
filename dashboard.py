import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Secure-Duka Analytics", layout="wide")

st.title("🛍️ Secure-Duka: Shop Intelligence")
st.markdown("---")

# 1. Fetch data from your FastAPI backend
try:
    report_res = requests.get("http://127.0.0.1:8000/analytics/restock-report/")
    report_data = report_res.json()
    
    # 2. Show Key Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Items Monitored", report_data['total_items_monitored'])
    with col2:
        urgent_count = len(report_data['urgent_restocks'])
        st.metric("Urgent Restocks", urgent_count, delta=-urgent_count, delta_color="inverse")

    # 3. Show the Restock Table
    st.subheader("⚠️ Inventory Warning List")
    if report_data['urgent_restocks']:
        df_report = pd.DataFrame(report_data['urgent_restocks'])
        st.table(df_report)
    else:
        st.success("All stock levels are healthy!")

except Exception as e:
    st.error("Could not connect to the Backend. Make sure FastAPI is running!")
    st.markdown("---")
st.subheader("📈 Sales Trend Analysis")

# Let the user pick a product to analyze
product_id = st.number_input("Enter Product ID to view trends", min_value=1, value=1)

try:
    # Call the forecast endpoint we built earlier
    trend_res = requests.get(f"http://127.0.0.1:8000/analytics/forecast/{product_id}")
    
    if trend_res.status_code == 200:
        data = trend_res.json()
        
        if "product" in data:
            st.write(f"Showing analysis for: **{data['product']}**")
            
            # Since we want to show a graph, let's fetch the actual sales history
            # For this, we'll assume you have a 'sales' list in your database or a separate endpoint
            # For now, let's display the velocity metric clearly
            st.info(f"The average sales velocity is **{data['avg_daily_velocity']}** units per day.")
            
            # Pro Tip: If you want a real graph, we can pull the raw sales data 
            # and use st.line_chart(df['qty'])
        else:
            st.warning(data['message'])
            
except Exception as e:
    st.error("Error fetching trend data.")
    # Add this to the sidebar of dashboard.py
st.sidebar.header("📦 Inventory Management")

with st.sidebar.form("restock_form"):
    p_id = st.number_input("Product ID", min_value=1, step=1)
    amount = st.number_input("Amount to Add", min_value=1, step=1)
    submitted = st.form_submit_button("Confirm Restock")
    
    if submitted:
        # Call the new restock endpoint
        res = requests.post(f"http://127.0.0.1:8000/products/restock/{p_id}?quantity={amount}")
        if res.status_code == 200:
            st.sidebar.success(res.json()['message'])
            # Trigger a refresh of the dashboard
            st.rerun()
        else:
            st.sidebar.error("Error updating stock.")