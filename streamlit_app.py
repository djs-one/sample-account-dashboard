import os

import pandas as pd
import streamlit as st
import plotly.express as px


def get_data():
    """Get account data"""
    xl = pd.ExcelFile("data/example.xlsx")
    sheets = xl.sheet_names
    dfd = {sheet: pd.read_excel(xl, sheet, index_col="DateTime", parse_dates=True) for sheet in sheets}
    df = pd.concat(dfd, axis=1)

    accts = df.columns.get_level_values(0).unique()
    cols = df.columns.get_level_values(1).unique()

    out = pd.DataFrame(index=df.index)
    for col in cols:
        try:
            acct1, acct2 = accts[0], accts[1]
            pd.testing.assert_series_equal(df[acct1][col], df[acct2][col])
            out[col] = df[acct1][col]
        except AssertionError:
            for acct in accts:
                out[f"{acct}-{col}"] = df[acct][col]

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
                