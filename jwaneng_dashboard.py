import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_ind

# -------------------------
# Load CSVs
# -------------------------
df = pd.read_csv("synthetic_jwaneng.csv")
sme_df = pd.read_csv("sme_jwaneng.csv")

# Convert 'date' column to proper datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# -------------------------
# App Title
# -------------------------
st.title("📊 Jwaneng Branch Case Study Dashboard")
st.write("Synthetic banking dataset for mine employees, SMEs, and digital channel usage.")

# -------------------------
# Dashboard Tab (3x3 Grid)
# -------------------------
st.header("📈 Key Insights Dashboard (3x3)")

# Create 3x3 grid
cols = st.columns(3)

# -------------------------
# Chart 1: Payroll Trend
# -------------------------
with cols[0].expander("💰 Payroll Trend"):
    payroll_df = df[df["category"] == "salary"].groupby("date")["amount"].sum().reset_index()
    payroll_df['rolling_avg'] = payroll_df['amount'].rolling(7).mean()
    fig = px.line(payroll_df, x='date', y='amount', title="Payroll Over Time")
    fig.add_scatter(x=payroll_df['date'], y=payroll_df['rolling_avg'], mode='lines', name='7-day Rolling Avg')
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 2: Channel Usage
# -------------------------
with cols[1].expander("📱 Channel Usage"):
    ch = df["channel"].value_counts().reset_index()
    ch.columns = ["channel", "count"]
    fig = px.bar(ch, x="channel", y="count", title="Channel Usage Distribution")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 3: Transaction Amounts
# -------------------------
with cols[2].expander("💵 Transaction Amounts"):
    fig = px.histogram(df, x="amount", nbins=50, title="Transaction Amount Distribution")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 4: SME Financing Trend
# -------------------------
with cols[0].expander("🏦 SME Financing Trend"):
    sme_trend = sme_df.groupby("date")["amount"].sum().reset_index()
    fig = px.line(sme_trend, x="date", y="amount", title="SME Financing Over Time")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 5: Payroll Hypothesis Test (Mine vs Non-Mine)
# -------------------------
with cols[1].expander("📊 Payroll: Mine vs Non-Mine"):
    mine_payroll = df[df['is_mine_employee'] == 'Yes']['amount']
    non_mine_payroll = df[df['is_mine_employee'] == 'No']['amount']
    t_stat, p_val = ttest_ind(mine_payroll, non_mine_payroll, equal_var=False)
    st.write(f"T-statistic: {t_stat:.2f}, P-value: {p_val:.4f}")
    if p_val < 0.05:
        st.write("Significant difference in payroll between mine and non-mine employees.")
    else:
        st.write("No significant difference in payroll between mine and non-mine employees.")

# -------------------------
# Chart 6: Channel Usage by Gender
# -------------------------
with cols[2].expander("👥 Channel Usage by Gender"):
    channel_gender = df.groupby(["gender", "channel"])["amount"].sum().reset_index()
    fig = px.bar(channel_gender, x="channel", y="amount", color="gender", barmode="group",
                 title="Channel Usage by Gender")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 7: Scatterplot Example
# -------------------------
with cols[0].expander("🔍 Amount vs Payroll"):
    fig = px.scatter(df[df['category']=='salary'], x="date", y="amount", color="is_mine_employee",
                     title="Salary Payments: Mine vs Non-Mine")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 8: SME vs Payroll Correlation
# -------------------------
with cols[1].expander("📈 SME vs Payroll"):
    merged = pd.merge(payroll_df, sme_trend, on="date", how="inner", suffixes=('_payroll','_sme'))
    fig = px.scatter(merged, x="amount_payroll", y="amount_sme",
                     title="Payroll vs SME Financing")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Chart 9: Digital Transactions Distribution
# -------------------------
with cols[2].expander("💻 Digital Transactions"):
    digital_df = df[df["channel"].isin(["Mobile", "Online", "ATM"])]
    fig = px.histogram(digital_df, x="amount", color="channel", nbins=50,
                       title="Digital Transactions by Channel")
    st.plotly_chart(fig, use_container_width=True)
