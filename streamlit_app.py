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
        df["Cost"] = df["Consumption"] * df["Spot Price"]
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
    st.set_page_config(layout="wide")
    st.title("Sample Dashboard")
    dfd = get_data()

    st.header("Settings", divider=True)

    freqd = {
        "Hourly": "h",
        "Daily": "d",
        "Weekly": "W",
        "Monthly": "ME",
    }

    # Frequency
    radiocols = st.columns(3)
    freq_radio = radiocols[0].radio(
        "Time Frequency",
        ["Monthly", "Weekly", "Daily", "Hourly"],
        index=1,
        horizontal=True,
    )

    methodd = {"Mean": "mean", "Median": "median", "Minimum": "min", "Maximum": "max"}
    method_radio = radiocols[1].radio("Method", list(methodd.keys()), horizontal=True)

    # Radio button to select accounts
    acct_radio = radiocols[2].radio("Accounts", [1, 2, "Sum"], horizontal=True, index=2)

    st.header("Basic time series", divider=True)

    # Create time series chart
    for i, (title, df) in enumerate(dfd.items()):
        st.subheader(title)  # Column used to center subheader
        rows = st.columns(2)
        # Time Series
        histdf = pd.DataFrame()
        funcs = ["sum"] if title == "Consumption" else ["min", "max", "mean"]
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
        rows[0].line_chart(
            histdf.reset_index(),
            x="DateTime",
            y=funcs,
            color="account" if "account" in histdf.columns else None,
            y_label=title,
            x_label=None,
        )

        # Filter to account if one selected
        if isinstance(acct_radio, int) and "account" in df.columns:
            df = df[df["account"] == acct_radio]
        df = df.drop(columns="account", errors="ignore")

        yoydf = (
            df.resample(f"1{freqd[freq_radio]}", on="DateTime")
            .apply(methodd[method_radio])
            .reset_index()
        )
        yoydf["DateTime"] = yoydf.reset_index()["DateTime"].apply(pd.to_datetime)

        # Create chart
        yoy = (
            alt.Chart(yoydf)
            .mark_line()
            .encode(
                x=alt.X("monthdate(DateTime):O").title("Date"),
                y=title,
                color=alt.Color("year(DateTime):O").title("Year"),
            )
        )
        rows[1].altair_chart(yoy)

    st.header("Correlations", divider=True)
    corrows = st.columns(3)

    # Create a scatter plot with relationship between prices and temp
    spottemp = pd.concat([dfd["Spot Price"], dfd["Temperature"]], axis=1)
    corrows[0].scatter_chart(spottemp, x="Temperature", y="Spot Price")

    # Get consumption - compare to temp/price
    con = dfd["Consumption"]

    for i, col in enumerate(["Temperature", "Spot Price"]):
        df = con.merge(dfd[col], left_index=True, right_index=True)
        corrows[i + 1].scatter_chart(df, x=col, y="Consumption", color="account")

    # Frequency radio button for account bar chart
    radiocol2 = st.columns(2)
    freq_radio2 = radiocol2[0].radio(
        "Time Frequency",
        ["Monthly", "Weekly", "Daily", "Hourly"],
        index=1,
        horizontal=True,
    )
    method_radio = radiocol2[1].radio("Method", list(methodd.keys()), horizontal=True)

    st.header("Account comparison", divider=True)
    accts = (
        dfd["Consumption"]
        .resample(f"1{freqd[freq_radio2]}")
        .apply(methodd[method_radio])
    )

    st.bar_chart(
        accts.reset_index(), x="DateTime", y="Consumption", color="account", stack=True
    )
