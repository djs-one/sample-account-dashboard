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
            dfd[col] = out

    return dfd

def get_figs(dfd):
    for i, val in enumerate(["Spot Price", "Temperature"]):
    #    fig.add_trace(px.line(dfd[val], x="DateTime", y=val), col=i, row=1)
        chart = alt.Chart(dfd[val]).mark_line().encode(x="DateTime", y=val)
        st.altair_chart(chart)
    
def set_frequency():
    pass

if __name__ == "__main__":
    st.title("Sample Dashboard")
    dfd = get_data()

    st.header("Spot Prices")
    
    freqd = {
        "Hour": "h",
        "Day": "d",
        "Week": "w",
        "Month": "m",
    }

    # Frequency
    freq_radio = st.radio("Time Frequency", ["Month", "Week", "Daily", "Hour"])
    method_radio = st.radio("Method", ["Mean", "Median", "Minimum", "Maximum", "Time"])

    hrs = dfd["Spot Price"].reset_index()["DateTime"].apply(lambda x: x.time()).unique()

    spotcharts = {}


    col1, col2 = st.columns(2)

    with col1:
        # Time Series
        spothist = dfd["Spot Price"].resample("")
        spotcharts["History"] = alt.Chart().mark_line().encode(x="DateTime", y="Spot Price")
        st.altair_chart(spotcharts["History"], title="History") 

    with col2:

        # YOY Chart
        spotcharts["Annual Comparison"] = alt.Chart(dfd["Spot Price"]).mark_line().encode(
            x=alt.X('monthdate(DateTime):O').title('Date'),
            y="Spot Price",
            color=alt.Color("year(DateTime):O").title("Year")
            )
        st.altair_chart(spotcharts["Annual Comparison"], title="Annual Comparison") 


    st.header("Accounts")

    
