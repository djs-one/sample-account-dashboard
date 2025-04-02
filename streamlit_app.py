import os

import altair as alt
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_data():
    """Get account data"""
    # Read each column into a DataFrame dictionary
    dfd = {}
    xl = pd.ExcelFile("data/example.xlsx")

    # Read each tab
    sheets = xl.sheet_names
    for sheet in sheets:
        df = pd.read_excel(xl, sheet, index_col="DateTime", parse_dates=True)
        for col in df.columns:
            out = df[col]
            out.name = sheet

            # Check if column has been added to the dfd
            if dfd.get(col) is not None:

                # If added, confirm new values in that column
                if out[dfd.get(col) != out].any():
                    dfs = [dfd[col], out]  # DataFrame list
                    for i, _sr in enumerate(dfs):
                        name = _sr.name.split("-")
                        _df = _sr.to_frame()
                        _df[name[0]] = name[1]
                        _df = _df.rename(columns={_sr.name: col})
                        dfs[i] = _df
                    out = pd.concat(dfs)
                    

                # Reset names in duplicated series
                else:
                    out.name = col
                    out = out.reset_index()
            dfd[col] = out

    return dfd

def get_figs(dfd):
    #fig = make_subplots(rows=3, cols=3)
    for i, val in enumerate(["Spot Price", "Temperature"]):
    #    fig.add_trace(px.line(dfd[val], x="DateTime", y=val), col=i, row=1)
        chart = alt.Chart(dfd[val]).mark_line().encode(x="DateTime", y=val)
        st.altair_chart(chart)

if __name__ == "__main__":
    st.title("Sample Dashboard")
    st.header("Accounts")

    dfd = get_data()
    figs = get_figs(dfd)
