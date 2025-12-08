# jwaneng_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("synthetic_jwaneng_prepared.csv", parse_dates=['date'])
    sme_df = pd.read_csv("sme_jwaneng.csv")
    return df, sme_df

df, sme_df = load_data()

# -----------------------------
# Sidebar / Landing Page
# -----------------------------
st.set_page_config(page_title="Jwaneng Branch Case Study", layout="wide")

st.title("🏦 Jwaneng Branch Case Study Dashboard")
st.markdown("""
Welcome! This dashboard explores synthetic banking transactions for FNB Jwaneng branch,
focusing on payroll patterns, SME financing, and digital banking adoption.
""")

# Quick overview charts
st.subheader("Overview Charts")
col1, col2 = st.columns(2)

# Total transaction amount over time
with col1:
    trans_over_time = df.groupby('date')['amount'].sum().reset_index()
    fig = px.line(trans_over_time, x='date', y='amount', title="Total Transactions Over Time")
    st.plotly_chart(fig, use_container_width=True)

# SME repayment status distribution
with col2:
    sme_counts = sme_df['repayment_status'].value_counts().reset_index()
    sme_counts.columns = ['repayment_status', 'count']
    fig2 = px.bar(sme_counts, x='repayment_status', y='count', title="SME Loan Repayment Status")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -----------------------------
# Tabs for Detailed Analysis
# -----------------------------
tabs = st.tabs(["Payroll", "SME Analysis", "Digital Banking", "Summary Stats", "Data Explorer"])

# -----------------------------
# Tab 1: Payroll Transactions
# -----------------------------
with tabs[0]:
    st.header("Payroll Transactions")
    payroll_df = df[df['category'] == 'salary']
    payroll_over_time = payroll_df.groupby('date')['amount'].sum().reset_index()
    fig_payroll = px.line(payroll_over_time, x='date', y='amount', title="Payroll Transaction Amounts Over Time")
    st.plotly_chart(fig_payroll, use_container_width=True)
    
    st.markdown("""
    **Insights:**  
    - Clear spikes on the 15th and end of each month, corresponding to paydays.  
    - Branch can anticipate high transaction volumes and optimize staffing & cash management.  
    - Opportunity for payday-linked micro-loans or digital savings campaigns.
    """)

# -----------------------------
# Tab 2: SME Analysis
# -----------------------------
with tabs[1]:
    st.header("SME Loan Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Repayment status bar chart
        rep_counts = sme_df['repayment_status'].value_counts().reset_index()
        rep_counts.columns = ['repayment_status', 'count']
        fig_sme1 = px.bar(rep_counts, x='repayment_status', y='count', title="SME Repayment Status")
        st.plotly_chart(fig_sme1, use_container_width=True)
    
    with col2:
        # Credit score vs loan amount
        fig_sme2 = px.scatter(sme_df, x='credit_score', y='loan_amount', color='repayment_status',
                              title="SME Credit Score vs Loan Amount", hover_data=['industry', 'sme_id'])
        st.plotly_chart(fig_sme2, use_container_width=True)
    
    st.markdown("""
    **Insights:**  
    - Most SMEs repay on time, but some default or pay late.  
    - Higher credit scores generally indicate timely repayment.  
    - Insights can guide risk-based SME lending strategies and industry-specific loan products.
    """)

# -----------------------------
# Tab 3: Digital Banking Channels
# -----------------------------
with tabs[2]:
    st.header("Digital Banking Adoption")
    channel_counts = df['channel'].value_counts().reset_index()
    channel_counts.columns = ['channel', 'count']
    fig_channel = px.bar(channel_counts, x='channel', y='count', title="Transactions by Channel")
    st.plotly_chart(fig_channel, use_container_width=True)

    # Payroll-specific channel usage
    payroll_channel_counts = payroll_df['channel'].value_counts().reset_index()
    payroll_channel_counts.columns = ['channel', 'count']
    fig_payroll_channel = px.bar(payroll_channel_counts, x='channel', y='count', title="Payroll Transactions by Channel")
    st.plotly_chart(fig_payroll_channel, use_container_width=True)

    st.markdown("""
    **Insights:**  
    - ATM and branch dominate for salary withdrawals.  
    - Mobile and USSD channels are underutilized, suggesting opportunity for digital adoption campaigns.  
    - Promoting digital channels can reduce branch congestion and improve efficiency.
    """)

# -----------------------------
# Tab 4: Summary Stats
# -----------------------------
with tabs[3]:
    st.header("Summary Statistics")
    st.subheader("Payroll Amounts")
    st.dataframe(payroll_df['amount'].describe())

    st.subheader("SME Loan Amounts")
    st.dataframe(sme_df['loan_amount'].describe())

    st.subheader("Transaction Amounts by Channel")
    st.dataframe(df.groupby('channel')['amount'].describe())

# -----------------------------
# Tab 5: Interactive Data Explorer
# -----------------------------
with tabs[4]:
    st.header("Explore the Data Yourself")
    st.markdown("Select X and Y axes to plot custom charts:")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    x_col = st.selectbox("X-axis", numeric_cols, index=0)
    y_col = st.selectbox("Y-axis", numeric_cols, index=1)
    chart_type = st.radio("Chart Type", ['Scatter', 'Line'])

    if chart_type == 'Scatter':
        fig_explore = px.scatter(df, x=x_col, y=y_col, color='channel', hover_data=['customer'])
    else:
        fig_explore = px.line(df, x=x_col, y=y_col, color='channel', hover_data=['customer'])

    st.plotly_chart(fig_explore, use_container_width=True)
    st.markdown("Use this tab to explore patterns and relationships across the dataset.")

