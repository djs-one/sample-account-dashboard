import os

import pandas as pd
import streamlit as st

def get_data():
    xl = pd.ExcelFile("data/example.xlsx")
    sheets = xl.sheet_names
    dfd = {sheet: pd.read_excel(xl, sheet).assign(account=sheet[-1]) for sheet in sheets}
    df = pd.concat(dfd, ignore_index=True)

    return df

st.title("Sample Dashboard")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
