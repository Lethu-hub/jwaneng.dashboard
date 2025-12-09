import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_ind
import os

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="Jwaneng Banking Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Helper function to safely load CSVs
# -------------------------
def load_csv(filename):
    if not os.path.exists(filename):
        st.warning(f"File not found: {filename}")
        return pd.DataFrame()  # return empty DataFrame if file missing
    df = pd.read_csv(filename)
    if df.empty:
        st.warning(f"File is empty: {filename}")
    return df
# -------------------------
# Load & Clean CSVs
# -------------------------
df = load_csv("synthetic_jwaneng.csv")
sme_df = load_csv("sme_jwaneng.csv")

# Convert 'date' columns and round to seconds to avoid PyArrow errors
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.floor('s')
if 'date' in sme_df.columns:
    sme_df['date'] = pd.to_datetime(sme_df['date'], errors='coerce').dt.floor('s')

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Dashboard",
    "🔍 EDA Explorer",
    "📑 Summary Statistics",
    "📚 Project Files"
])

# -------------------------
# TAB 1: DASHBOARD (3x3)
# -------------------------
with tab1:
    st.title("📊 Jwaneng Branch Dashboard (3x3)")

    # Helper to plot in columns
    def plot_chart(fig, col):
        with col:
            st.plotly_chart(fig, use_container_width=True)

    # 3x3 layout
    rows = [st.columns(3) for _ in range(3)]

    # -------- Row 1 --------
    # Chart 1: Payroll Trend
    payroll_df = df[df["category"] == "salary"].groupby("date")["amount"].sum().reset_index()
    payroll_df['rolling_avg'] = payroll_df['amount'].rolling(7).mean()
    fig1 = px.line(payroll_df, x='date', y='amount', title="💰 Payroll Trend")
    fig1.add_scatter(x=payroll_df['date'], y=payroll_df['rolling_avg'], mode='lines', name='7-day Rolling Avg')
    plot_chart(fig1, rows[0][0])

    # Chart 2: Channel Usage
    ch = df["channel"].value_counts().reset_index()
    ch.columns = ["channel", "count"]
    fig2 = px.bar(ch, x="channel", y="count", title="📱 Channel Usage")
    plot_chart(fig2, rows[0][1])

    # Chart 3: Transaction Amount Distribution
    fig3 = px.histogram(df, x="amount", nbins=50, title="💵 Transaction Amounts")
    plot_chart(fig3, rows[0][2])

    # -------- Row 2 --------
    # Chart 4: SME Financing Trend
    if 'date' in sme_df.columns:
        sme_trend = sme_df.groupby("date")["amount"].sum().reset_index()
        fig4 = px.line(sme_trend, x="date", y="amount", title="🏦 SME Financing Trend")
        plot_chart(fig4, rows[1][0])
    else:
        rows[1][0].warning("SME dataset missing 'date' column!")

    # Chart 5: Payroll Hypothesis Test (Mine vs Non-Mine)
    mine_payroll = df[df['is_mine_employee'] == 'Yes']['amount']
    non_mine_payroll = df[df['is_mine_employee'] == 'No']['amount']
    t_stat, p_val = ttest_ind(mine_payroll, non_mine_payroll, equal_var=False)
    fig5 = px.bar(x=["Mine", "Non-Mine"], y=[mine_payroll.mean(), non_mine_payroll.mean()],
                  title=f"📊 Payroll: Mine vs Non-Mine (p={p_val:.3f})")
    plot_chart(fig5, rows[1][1])

    # Chart 6: Channel Usage by Gender
    channel_gender = df.groupby(["gender", "channel"])["amount"].sum().reset_index()
    fig6 = px.bar(channel_gender, x="channel", y="amount", color="gender", barmode="group",
                  title="👥 Channel Usage by Gender")
    plot_chart(fig6, rows[1][2])

    # -------- Row 3 --------
    # Chart 7: Salary Scatterplot
    fig7 = px.scatter(df[df['category'] == 'salary'], x="date", y="amount", color="is_mine_employee",
                      title="🔍 Salary Payments: Mine vs Non-Mine")
    plot_chart(fig7, rows[2][0])

    # Chart 8: SME vs Payroll Correlation
    if 'date' in sme_df.columns:
        merged = pd.merge(payroll_df, sme_trend, on="date", how="inner", suffixes=('_payroll','_sme'))
        fig8 = px.scatter(merged, x="amount_payroll", y="amount_sme", title="📈 Payroll vs SME")
        plot_chart(fig8, rows[2][1])
    else:
        rows[2][1].warning("SME dataset missing 'date' column!")

    # Chart 9: Digital Transactions
    digital_df = df[df["channel"].isin(["Mobile", "Online", "ATM"])]
    fig9 = px.histogram(digital_df, x="amount", color="channel", nbins=50, title="💻 Digital Transactions")
    plot_chart(fig9, rows[2][2])

# -------------------------
# TAB 2: EDA Explorer
# -------------------------
with tab2:
    st.header("🔍 Explore the Data Yourself")
    col1, col2 = st.columns(2)
    x_var = col1.selectbox("Select X variable", df.columns)
    y_var = col2.selectbox("Select Y variable", df.columns)
    fig_custom = px.scatter(df, x=x_var, y=y_var, title=f"Scatter Plot: {x_var} vs {y_var}")
    st.plotly_chart(fig_custom, use_container_width=True)
    st.markdown("Use this tool to explore correlations, trends, and anomalies.")

# -------------------------
# TAB 3: Summary Statistics
# -------------------------
with tab3:
    st.header("📑 Summary Statistics")
    st.subheader("Numeric Columns")
    st.write(df.describe())
    st.subheader("Categorical Counts")
    for col in ["gender", "category", "channel", "is_mine_employee"]:
        st.write(f"### {col}")
        st.write(df[col].value_counts())

# -------------------------
# TAB 4: Project Files
# -------------------------
with tab4:
    st.header("📚 Project Documents")
    st.markdown("Download the full project files for details on the dataset, analysis, and notebook.")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    pdf_explanation_path = os.path.join(BASE_DIR, "Simple Bank Data Project Explanation.pdf")
    if os.path.exists(pdf_explanation_path):
        with open(pdf_explanation_path, "rb") as f:
            st.download_button(
                label="Download Project Explanation PDF",
                data=f,
                file_name="Simple Bank Data Project Explanation.pdf",
                mime="application/pdf"
            )
    else:
        st.warning(f"File not found: {pdf_explanation_path}")

    pdf_analysis_path = os.path.join(BASE_DIR, "Simple Bank Data Analysis - Colab.pdf")
    if os.path.exists(pdf_analysis_path):
        with open(pdf_analysis_path, "rb") as f:
            st.download_button(
                label="Download Analysis Notebook PDF",
                data=f,
                file_name="Simple Bank Data Analysis - Colab.pdf",
                mime="application/pdf"
            )
    else:
        st.warning(f"File not found: {pdf_analysis_path}")
