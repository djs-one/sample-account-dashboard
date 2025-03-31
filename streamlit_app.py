import os

import pandas as pd
import streamlit as st

def get_data():
    xl = pd.ExcelFile("data/example.xlsx")
    sheets = xl.sheet_names
    dfd = {sheet: pd.read_excel(xl, sheet).assign(account=sheet[-1]) for sheet in sheets}
    df = pd.concat(dfd, ignore_index=True)

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
    st.line_chart(df, x="DateTime", y=col)