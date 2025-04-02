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
                # Ex. don't duplicate temperature columns if equal
                if out[dfd.get(col) != out].any():
                    dfs = [dfd[col], out]  # DataFrame list
                    for i, _sr in enumerate(dfs):
                        name = _sr.name.split("-")
                        _df = _sr.to_frame()
                        _df[name[0]] = int(name[1])
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
        "Hourly": "h",
        "Daily": "d",
        "Weekly": "W",
        "Monthly": "ME",
    }

    # Frequency
    freq_radio = st.radio(
        "Time Frequency", ["Monthly", "Weekly", "Daily", "Hourly"], index=2
    )
    method_radio = st.radio("Method", ["Mean", "Median", "Minimum", "Maximum", "Time"])

    hrs = dfd["Spot Price"].reset_index()["DateTime"].apply(lambda x: x.time()).unique()

    rows = st.columns(3) + st.columns(3)

    # Create chart in each of 3 columns
    for i, (title, df) in enumerate(dfd.items()):

        # Time Series
        histdf = pd.DataFrame()
        funcs = ["min", "max", "mean"]
        for func in funcs:
            df = dfd[title].reset_index()

            histdf[func] = df.resample(f"1{freqd[freq_radio]}", on="DateTime")[
                title
            ].apply(func)

        histchart = (
            alt.Chart(histdf.melt(ignore_index=False).reset_index())
            .mark_line()
            .encode(
                x=alt.X("yearmonthdate(DateTime):O").title("Date"),
                y=alt.Y("value").title(title),
                color="variable",
            )
        )
        # row1[0].altair_chart(histchart)
        rows[i].line_chart(
            histdf.reset_index(),
            x="DateTime",
            y=["min", "max", "mean"],
            color="account" if "account" in histdf.columns else None,
        )

        yoydf = df.resample(f"1{freqd[freq_radio]}", on="DateTime").apply(
            method_radio.lower()
        )

        color = alt.Color("year(DateTime):O").title("Year")
        if "account" in histdf.columns:
            color += ["account"]

        yoy = (
            alt.Chart(yoydf)
            .mark_line()
            .encode(
                x=alt.X("monthdate(DateTime):O").title("Date"), y=title, color=color
            )
        )
        rows[i + 1].altair_chart(yoy)
