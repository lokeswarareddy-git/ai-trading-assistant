import streamlit as st
import requests
import pandas as pd

API_URL = "https://ai-trading-assistant-2ji8.onrender.com"

st.set_page_config(
    page_title="AI Trading Journal",
    layout="wide",
    page_icon="📈"
)

# -------------------------
# Helper: Fetch Trades
# -------------------------
@st.cache_data(ttl=10)
def fetch_trades():
    try:
        res = requests.get(f"{API_URL}/trades")
        return res.json() if res.status_code == 200 else []
    except:
        return []

data = fetch_trades()
df = pd.DataFrame(data)

# -------------------------
# Sidebar Navigation
# -------------------------
st.sidebar.title("📊 Menu")
page = st.sidebar.radio("", ["Dashboard", "Trades", "Insights"])

st.title("📈 AI Trading Assistant")

# -------------------------
# ADD TRADE (GLOBAL - always visible)
# -------------------------
st.subheader("➕ Add Trade")

col1, col2, col3, col4 = st.columns(4)

with col1:
    symbol = st.text_input("Symbol")

with col2:
    side = st.selectbox("Side", ["BUY", "SELL"])

with col3:
    entry = st.number_input("Entry Price")

with col4:
    exit_price = st.number_input("Exit Price")

qty = st.number_input("Quantity", step=1)

strategy = st.text_input("Strategy")
notes = st.text_area("Notes")

if st.button("Submit Trade"):
    payload = {
        "symbol": symbol,
        "side": side,
        "strategy": strategy,
        "entry_price": entry,
        "exit_price": exit_price,
        "quantity": int(qty),
        "notes": notes
    }

    try:
        res = requests.post(f"{API_URL}/trade", json=payload)

        if res.status_code == 200:
            st.success("Trade added ✅")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(f"Failed: {res.text}")

    except Exception as e:
        st.error(str(e))

st.divider()

# -------------------------
# DASHBOARD
# -------------------------
if page == "Dashboard":
    st.header("📊 Dashboard")

    if not df.empty:
        col1, col2, col3 = st.columns(3)

        total_trades = len(df)
        total_pnl = df["pnl"].sum() if "pnl" in df else 0
        win_rate = (df["pnl"] > 0).mean() * 100 if "pnl" in df else 0

        col1.metric("Total Trades", total_trades)
        col2.metric("Total PnL", round(total_pnl, 2))
        col3.metric("Win Rate %", round(win_rate, 2))

        st.subheader("📈 PnL Chart")
        st.line_chart(df["pnl"])

    else:
        st.info("No trades yet")

# -------------------------
# TRADES TABLE
# -------------------------
elif page == "Trades":
    st.header("📋 Trades")

    if not df.empty:
        columns = [
            "id", "symbol", "side", "strategy",
            "entry_price", "exit_price",
            "quantity", "pnl", "notes"
        ]

        df = df.reindex(columns=columns)

        def color_pnl(val):
            if val > 0:
                return "color: green"
            elif val < 0:
                return "color: red"
            return ""

        st.dataframe(df.style.applymap(color_pnl, subset=["pnl"]),
                     use_container_width=True)
    else:
        st.info("No trades found")

# -------------------------
# INSIGHTS
# -------------------------
elif page == "Insights":
    st.header("🤖 Insights")

    if not df.empty:
        selected = st.selectbox("Select Trade", df.index)

        if st.button("Analyze"):
            trade = df.iloc[selected].to_dict()

            try:
                res = requests.post(f"{API_URL}/analyze", json=trade)

                if res.status_code == 200:
                    st.write(res.json())
                else:
                    st.error("Analysis failed")
            except Exception as e:
                st.error(str(e))
    else:
        st.info("No data available")