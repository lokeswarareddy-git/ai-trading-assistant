import streamlit as st
import requests
import pandas as pd

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

def add_trade_ui():
    st.header("➕ Add Trade")

    side = st.selectbox("Side", ["BUY", "SELL"])

    if st.button("Submit Trade"):
        payload = {
            "side": side
        }

        res = requests.post(f"{API_URL}/trade", json=payload)

        if res.status_code == 200:
            st.success("Trade added successfully!")
            st.json(res.json())
        else:
            st.error(res.text)


def view_trades_ui():
    st.header("📊 All Trades")

    if st.button("Load Trades"):
        res = requests.get(f"{API_URL}/trades")

        if res.status_code == 200:
            trades = res.json()
            df = pd.DataFrame(trades)
            st.dataframe(df)
        else:
            st.error("Failed to fetch trades")


def main():
    st.set_page_config(page_title="Trading Journal", layout="wide")

    st.title("📈 AI Trading Assistant")

    menu = st.sidebar.selectbox("Menu", ["Add Trade", "View Trades"])

    if menu == "Add Trade":
        add_trade_ui()

    elif menu == "View Trades":
        view_trades_ui()


if __name__ == "__main__":
    main()