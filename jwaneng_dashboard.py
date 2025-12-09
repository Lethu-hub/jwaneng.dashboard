import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -------------------------
# Base directory (script folder)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------
# Helper to safely load CSVs
# -------------------------
def load_csv(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        st.warning(f"File not found: {filepath}")
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    if df.empty:
        st.warning(f"File is empty: {filepath}")
    return df

# -------------------------
# Load CSVs
# -------------------------
df = load_csv("synthetic_jwaneng.csv")
sme_df = load_csv("sme_jwaneng.csv")

# -------------------------
# Convert date columns safely
# -------------------------
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.floor('s')
if 'date' in sme_df.columns:
    sme_df['date'] = pd.to_datetime(sme_df['date'], errors='coerce').dt.floor('s')

# -------------------------
# App Title
# -------------------------
st.set_page_config(layout="wide")
st.title("📊 Jwaneng Branch Case Study Dashboard")

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Key Insights",
    "🔍 EDA Explorer",
    "📑 Summary Statistics",
    "💾 Downloads"
])

# -------------------------
# TAB 1: Key Insights (3x3 mini charts)
# -------------------------
with tab1:
    st.header("Key Insights")
    
    cols = st.columns(3)
    
    # Chart 1: Payroll Trend
    if "salary" in df["category"].unique():
        payroll_df = df[df["category"] == "salary"]
        payroll_daily = payroll_df.groupby("date")["amount"].sum().reset_index()
        fig1 = px.line(payroll_daily, x="date", y="amount", title="Payroll Trend")
        cols[0].plotly_chart(fig1, width='stretch')

    # Chart 2: Channel Distribution
    ch = df["channel"].value_counts().reset_index()
    ch.columns = ["channel", "count"]
    fig2 = px.bar(ch, x="channel", y="count", title="Channel Usage")
    cols[1].plotly_chart(fig2, width='stretch')

    # Chart 3: Transaction Amount Distribution
    fig3 = px.histogram(df, x="amount", nbins=50, title="Transaction Amounts")
    cols[2].plotly_chart(fig3, width='stretch')

    # Chart 4: SME Financing Trend
    if not sme_df.empty and 'date' in sme_df.columns:
        sme_trend = sme_df.groupby("date")["loan_amount"].sum().reset_index()
        fig4 = px.line(sme_trend, x="date", y="loan_amount", title="SME Financing Trend")
        cols[0].plotly_chart(fig4, width='stretch')

    # Chart 5: SME Credit Score Distribution
    if 'credit_score' in sme_df.columns:
        fig5 = px.histogram(sme_df, x="credit_score", nbins=20, title="SME Credit Scores")
        cols[1].plotly_chart(fig5, width='stretch')

    # Chart 6: SME Repayment Status Counts
    if 'repayment_status' in sme_df.columns:
        rep_count = sme_df['repayment_status'].value_counts().reset_index()
        rep_count.columns = ['repayment_status', 'count']
        fig6 = px.bar(rep_count, x='repayment_status', y='count', title="Repayment Status")
        cols[2].plotly_chart(fig6, width='stretch')

    # Chart 7: Gender Distribution
    if 'gender' in df.columns:
        fig7 = px.pie(df, names='gender', title="Gender Distribution")
        cols[0].plotly_chart(fig7, width='stretch')

    # Chart 8: Payroll vs Mine Employee
    if 'is_mine_employee' in df.columns:
        payroll_emp = df[df["category"]=="salary"].groupby("is_mine_employee")["amount"].sum().reset_index()
        fig8 = px.bar(payroll_emp, x="is_mine_employee", y="amount", title="Payroll by Mine Employee")
        cols[1].plotly_chart(fig8, width='stretch')

    # Chart 9: Transaction Count by Category
    cat_count = df["category"].value_counts().reset_index()
    cat_count.columns = ["category", "count"]
    fig9 = px.bar(cat_count, x="category", y="count", title="Transactions by Category")
    cols[2].plotly_chart(fig9, width='stretch')

# -------------------------
# TAB 2: EDA Explorer (full interactive)
# -------------------------
with tab2:
    st.header("🔍 Explore the Data")
    if not df.empty:
        st.markdown("Select variables, chart type, and options below:")

        col1, col2, col3, col4 = st.columns(4)

        # Variable selectors
        x_var = col1.selectbox("X variable", df.columns)
        y_var = col2.selectbox("Y variable (optional)", [None] + list(df.columns))
        chart_type = col3.selectbox(
            "Chart type",
            ["Scatter", "Line", "Bar", "Cumulative Bar", "Cumulative Line",
             "Histogram", "Pie", "Box", "Violin"]
        )
        cumulative = col4.checkbox("Cumulative?", value=False)

        fig = None
        # ---------------------
        # Generate chart based on user selection
        # ---------------------
        if chart_type in ["Scatter", "Line", "Bar", "Cumulative Bar", "Cumulative Line"] and y_var:
            plot_df = df.copy()
            if cumulative and chart_type in ["Cumulative Bar", "Cumulative Line"]:
                plot_df = plot_df.groupby(x_var)[y_var].sum().reset_index()
                plot_df[y_var] = plot_df[y_var].cumsum()
            if chart_type in ["Scatter"]:
                fig = px.scatter(plot_df, x=x_var, y=y_var, title=f"Scatter: {x_var} vs {y_var}")
            elif chart_type in ["Line", "Cumulative Line"]:
                fig = px.line(plot_df, x=x_var, y=y_var, title=f"Line: {x_var} vs {y_var}")
            elif chart_type in ["Bar", "Cumulative Bar"]:
                fig = px.bar(plot_df, x=x_var, y=y_var, title=f"Bar: {x_var} vs {y_var}")
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=x_var, title=f"Histogram: {x_var}")
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_var, title=f"Pie: {x_var}")
        elif chart_type == "Box":
            if y_var:
                fig = px.box(df, x=x_var, y=y_var, title=f"Box Plot: {x_var} vs {y_var}")
        elif chart_type == "Violin":
            if y_var:
                fig = px.violin(df, x=x_var, y=y_var, title=f"Violin Plot: {x_var} vs {y_var}")

        if fig:
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Select a Y variable for this chart type if needed.")

# -------------------------
# TAB 3: Summary Statistics
# -------------------------
with tab3:
    st.header("Summary Statistics")
    if not df.empty:
        st.subheader("Numeric Columns")
        st.write(df.describe())
        st.subheader("Categorical Counts")
        for col in ["gender", "category", "channel", "is_mine_employee"]:
            if col in df.columns:
                st.write(f"### {col}")
                st.write(df[col].value_counts())

# -------------------------
# TAB 4: Downloads
# -------------------------
with tab4:
    st.header("Project Files")
    files = [
        "Simple Bank Data Analysis - Colab.pdf",
        "Simple Bank Data Project Explanation.pdf"
    ]
    for f in files:
        filepath = os.path.join(BASE_DIR, f)
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                st.download_button(label=f"Download {f}", data=file)
        else:
            st.warning(f"File not found: {f}")
