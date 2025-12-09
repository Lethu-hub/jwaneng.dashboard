import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_ind

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="Jwaneng Banking Dashboard",
    layout="wide",  # full-width layout
    initial_sidebar_state="expanded"
)

# -------------------------
# Load CSVs
# -------------------------
df = pd.read_csv("synthetic_jwaneng.csv")
sme_df = pd.read_csv("sme_jwaneng.csv")

# Convert 'date' columns to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')
if 'date' in sme_df.columns:
    sme_df['date'] = pd.to_datetime(sme_df['date'], errors='coerce')

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
    "📚 Project Files"
])

# ---------------------------------------------------
# TAB 1: DASHBOARD (3x3 Grid)
# ---------------------------------------------------
with tab1:
    st.header("📈 Key Insights")

    # 3 columns per row, 3 rows → total 9 charts
    rows = [st.columns(3) for _ in range(3)]

    # -------- Chart 1: Payroll Trend with Rolling Avg --------
    with rows[0][0].expander("💰 Payroll Trend"):
        payroll_df = df[df["category"] == "salary"].groupby("date")["amount"].sum().reset_index()
        payroll_df['rolling_avg'] = payroll_df['amount'].rolling(7).mean()
        fig = px.line(payroll_df, x='date', y='amount', title="Payroll Over Time")
        fig.add_scatter(x=payroll_df['date'], y=payroll_df['rolling_avg'], mode='lines', name='7-day Rolling Avg')
        st.plotly_chart(fig, use_container_width=True)

    # -------- Chart 2: Channel Usage --------
    with rows[0][1].expander("📱 Channel Usage"):
        ch = df["channel"].value_counts().reset_index()
        ch.columns = ["channel", "count"]
        fig = px.bar(ch, x="channel", y="count", title="Channel Usage Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # -------- Chart 3: Transaction Amount Distribution --------
    with rows[0][2].expander("💵 Transaction Amounts"):
        fig = px.histogram(df, x="amount", nbins=50, title="Transaction Amount Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # -------- Chart 4: SME Financing Trend --------
    with rows[1][0].expander("🏦 SME Financing Trend"):
        if 'date' in sme_df.columns:
            sme_trend = sme_df.groupby("date")["amount"].sum().reset_index()
            fig = px.line(sme_trend, x="date", y="amount", title="SME Financing Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("SME dataset missing 'date' column!")

    # -------- Chart 5: Payroll Hypothesis Test (Mine vs Non-Mine) --------
    with rows[1][1].expander("📊 Payroll: Mine vs Non-Mine"):
        mine_payroll = df[df['is_mine_employee'] == 'Yes']['amount']
        non_mine_payroll = df[df['is_mine_employee'] == 'No']['amount']
        t_stat, p_val = ttest_ind(mine_payroll, non_mine_payroll, equal_var=False)
        st.write(f"T-statistic: {t_stat:.2f}, P-value: {p_val:.4f}")
        if p_val < 0.05:
            st.write("Significant difference in payroll between mine and non-mine employees.")
        else:
            st.write("No significant difference in payroll between mine and non-mine employees.")

    # -------- Chart 6: Channel Usage by Gender --------
    with rows[1][2].expander("👥 Channel Usage by Gender"):
        channel_gender = df.groupby(["gender", "channel"])["amount"].sum().reset_index()
        fig = px.bar(channel_gender, x="channel", y="amount", color="gender", barmode="group",
                     title="Channel Usage by Gender")
        st.plotly_chart(fig, use_container_width=True)

    # -------- Chart 7: Salary Scatterplot (Mine vs Non-Mine) --------
    with rows[2][0].expander("🔍 Salary Scatterplot"):
        fig = px.scatter(df[df['category'] == 'salary'], x="date", y="amount", color="is_mine_employee",
                         title="Salary Payments: Mine vs Non-Mine")
        st.plotly_chart(fig, use_container_width=True)

    # -------- Chart 8: SME vs Payroll Correlation --------
    with rows[2][1].expander("📈 SME vs Payroll"):
        if 'date' in sme_df.columns:
            merged = pd.merge(payroll_df, sme_trend, on="date", how="inner", suffixes=('_payroll','_sme'))
            fig = px.scatter(merged, x="amount_payroll", y="amount_sme", title="Payroll vs SME Financing")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("SME dataset missing 'date' column!")

    # -------- Chart 9: Digital Transactions --------
    with rows[2][2].expander("💻 Digital Transactions"):
        digital_df = df[df["channel"].isin(["Mobile", "Online", "ATM"])]
        fig = px.histogram(digital_df, x="amount", color="channel", nbins=50,
                           title="Digital Transactions by Channel")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# TAB 2: EXPLORATORY DATA ANALYSIS (keep as-is)
# ---------------------------------------------------
with tab2:
    st.header("🔍 Explore the Data Yourself")
    col1, col2 = st.columns(2)

    x_var = col1.selectbox("Select X variable", df.columns)
    y_var = col2.selectbox("Select Y variable", df.columns)

    fig_custom = px.scatter(df, x=x_var, y=y_var, title=f"Scatter Plot: {x_var} vs {y_var}")
    st.plotly_chart(fig_custom, use_container_width=True)
    st.markdown("Use this tool to explore correlations, trends, and anomalies.")

# ---------------------------------------------------
# TAB 3: SUMMARY STATISTICS (keep as-is)
# ---------------------------------------------------
with tab3:
    st.header("📑 Summary Statistics")

    st.subheader("Numeric Columns")
    st.write(df.describe())

    st.subheader("Categorical Counts")
    for col in ["gender", "category", "channel", "is_mine_employee"]:
        st.write(f"### {col}")
        st.write(df[col].value_counts())

# ---------------------------------------------------
# TAB 4: PROJECT FILES (Download PDFs)
# ---------------------------------------------------
with tab4:
    st.header("📚 Project Documents")
    st.markdown("Download the full project files for details on the dataset, analysis, and notebook.")

    # Case study explanation PDF
    with open("Simple_Bank_Data_Project_Explanation.pdf", "rb") as f:
        st.download_button(
            label="Download Project Explanation PDF",
            data=f,
            file_name="Simple_Bank_Data_Project_Explanation.pdf",
            mime="application/pdf"
        )

    # Notebook/Analysis PDF
    with open("Simple_Bank_Data_Analysis_Colab.pdf", "rb") as f:
        st.download_button(
            label="Download Analysis Notebook PDF",
            data=f,
            file_name="Simple_Bank_Data_Analysis_Colab.pdf",
            mime="application/pdf"
        )
