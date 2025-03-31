import os

import pandas as pd
import streamlit as st
import plotly.express as px


def get_data():
    xl = pd.ExcelFile("data/example.xlsx")
    sheets = xl.sheet_names
    dfd = {sheet: pd.read_excel(xl, sheet).assign(account=sheet[-1]) for sheet in sheets}
    df = pd.concat(dfd, ignore_index=True)
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    return df

df = get_data()

st.title("Sample Dashboard")

# Create checkboxes to 
st.write("Accounts")
for account in df["account"].unique():
    st.checkbox(account)

cols = df.columns[1:-1]
for col in cols:
    st.header(col)
    fig = px.line(df, x='DateTime', y=col, color='account')
    st.plotly_chart(fig)
                