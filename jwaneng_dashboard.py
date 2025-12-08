import streamlit as st
import pandas as pd
import plotly.express as px

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
# Navigation Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Dashboard",
    "🔍 EDA Explorer",
    "📑 Summary Statistics",
    "🗂️ Raw Data"
])

# ---------------------------------------------------
# TAB 1: DASHBOARD
# ---------------------------------------------------
with tab1:
    st.header("📈 Key Insights Dashboard")

    # Payroll Trend (salary category only)
    if "salary" in df["category"].unique():
        payroll_df = df[df["category"] == "salary"]
        payroll_daily = payroll_df.groupby("date")["amount"].sum().reset_index()

        fig_payroll = px.line(
            payroll_daily, x="date", y="amount",
            title="💰 Payroll Spikes (15th & Month End)"
        )
        st.plotly_chart(fig_payroll, width='stretch')

    # Channel distribution
    ch = df["channel"].value_counts().reset_index()
    ch.columns = ["channel", "count"]

    fig_channel = px.bar(
        ch, x="channel", y="count",
        title="📱 Channel Usage Distribution"
    )
    st.plotly_chart(fig_channel, width='stretch')

    # Amount distribution
    fig_amount = px.histogram(
        df, x="amount", nbins=50,
        title="💵 Transaction Amount Distribution"
    )
    st.plotly_chart(fig_amount, width='stretch')

# ---------------------------------------------------
# TAB 2: EXPLORATORY DATA ANALYSIS
# ---------------------------------------------------
with tab2:
    st.header("🔍 Explore the Data Yourself")
    col1, col2 = st.columns(2)

    x_var = col1.selectbox("Select X variable", df.columns)
    y_var = col2.selectbox("Select Y variable", df.columns)

    fig_custom = px.scatter(
        df, x=x_var, y=y_var,
        title=f"Scatter Plot: {x_var} vs {y_var}"
    )
    st.plotly_chart(fig_custom, width='stretch')
    st.markdown("Use this tool to explore correlations, trends, and anomalies.")

# ---------------------------------------------------
# TAB 3: SUMMARY STATISTICS
# ---------------------------------------------------
with tab3:
    st.header("📑 Summary Statistics")

    st.subheader("Numeric Columns")
    st.write(df.describe())

    st.subheader("Categorical Counts")
    for col in ["gender", "category", "channel", "is_mine_employee"]:
        st.write(f"### {col}")
        st.write(df[col].value_count_)
