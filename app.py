import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="HR Attrition Analytics", layout="wide")
st.title("📊 IBM HR Employee Attrition Analytics")

# Load Data (SQL Server locally, CSV fallback for Streamlit Cloud)
@st.cache_data
def load_data():
    try:
        server = 'localhost'
        database = 'HR_Analytics'
        conn_str = (
            f"mssql+pyodbc://{server}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        )
        engine = create_engine(conn_str)
        return pd.read_sql("SELECT * FROM hr_emp_attrition", con=engine)
    except Exception:
        # Fallback for Streamlit Cloud
        df = pd.read_csv('data/hr_attrition.csv')
        df.columns = df.columns.str.strip().str.replace('([a-z0-9])([A-Z])', r'\1_\2', regex=True).str.lower()
        df['attrition_num'] = df['attrition'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
        satisfaction_map = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very High'}
        df['job_satisfaction_label'] = df['job_satisfaction'].map(satisfaction_map)
        return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_dept = st.sidebar.multiselect("Department", options=df["department"].unique(), default=df["department"].unique())
selected_overtime = st.sidebar.multiselect("Overtime Status", options=df["over_time"].unique(), default=df["over_time"].unique())

filtered_df = df[(df["department"].isin(selected_dept)) & (df["over_time"].isin(selected_overtime))]

# KPIs
total_emp = len(filtered_df)
total_attrition = filtered_df["attrition_num"].sum()
attrition_rate = (total_attrition / total_emp * 100) if total_emp > 0 else 0
avg_income = filtered_df["monthly_income"].mean() if total_emp > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees", f"{total_emp:,}")
col2.metric("Total Attrition", f"{total_attrition:,}")
col3.metric("Attrition Rate", f"{attrition_rate:.1f}%")
col4.metric("Avg Monthly Income", f"${avg_income:,.0f}")

st.markdown("---")

# Visualizations
c1, c2 = st.columns(2)

with c1:
    st.subheader("Attrition Rate by Department")
    dept_summary = filtered_df.groupby("department")["attrition_num"].mean().reset_index()
    dept_summary["rate"] = dept_summary["attrition_num"] * 100
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=dept_summary, x="department", y="rate", palette="magma", ax=ax1)
    ax1.set_ylabel("Attrition Rate (%)")
    ax1.set_xlabel("")
    st.pyplot(fig1)

with c2:
    st.subheader("Attrition Rate by Job Satisfaction")
    sat_summary = filtered_df.groupby("job_satisfaction_label")["attrition_num"].mean().reset_index()
    sat_summary["rate"] = sat_summary["attrition_num"] * 100
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=sat_summary, x="job_satisfaction_label", y="rate", order=["Low", "Medium", "High", "Very High"], palette="viridis", ax=ax2)
    ax2.set_ylabel("Attrition Rate (%)")
    ax2.set_xlabel("")
    st.pyplot(fig2)

with st.expander("📄 View SQL Data"):
    st.dataframe(filtered_df)