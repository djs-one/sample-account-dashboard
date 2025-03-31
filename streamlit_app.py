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

st.write("Accounts")
for account in df["account"].unique():
    st.checkbox(account)

st.line_chart(df)