import streamlit as st
import pandas as pd

@st.cache_data(ttl=60)
def carregar_planilha(sheet_name: str) -> pd.DataFrame:
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    except KeyError:
        st.error("❌ Secret GOOGLE_SHEET_ID não configurado.")
        st.stop()

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    df = pd.read_csv(url, on_bad_lines="skip")
    df = df.dropna(how="all", axis=1).dropna(how="all", axis=0)

    df.columns = [c.strip().capitalize() for c in df.columns]

    if "Data" in df.columns:
        df["Data_dt"] = pd.to_datetime(df["Data"], errors="coerce")

    return df
