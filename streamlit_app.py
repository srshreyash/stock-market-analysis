import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("Stock Market Dashboard")
st.write("Ellaam Maayai")

st.sidebar.header("Ticker settings")
# Default ticker set to a known NSE symbol so the app runs reliably
default_ticker = "RELIANCE.NS"
ticker_input = st.sidebar.text_input("Ticker (Yahoo Finance)", value=default_ticker)

st.sidebar.markdown("Choose date range or leave empty to use full available history (since IPO).")
start_default = (datetime.today().date() - timedelta(days=365))
start_date = st.sidebar.date_input("Start date", value=start_default)
end_date = st.sidebar.date_input("End date", value=datetime.today().date())

if st.sidebar.button("Fetch and plot"):
    with st.spinner("Fetching data from Yahoo Finance..."):
        try:
            tk = yf.Ticker(ticker_input)
            # Get full history
            hist = tk.history(period="max", interval="1d")

            # Try to determine IPO date from info if available
            info = tk.info if hasattr(tk, "info") else {}
            ipo_date = None
            if isinstance(info, dict):
                ipo_date = info.get("ipoDate") or info.get("firstTradeDateEpochUtc")
                # if epoch provided, convert to date
                if isinstance(ipo_date, (int, float)):
                    try:
                        ipo_date = datetime.utcfromtimestamp(int(ipo_date)).date()
                    except Exception:
                        ipo_date = None

            # If user provided a start date, use it; else if ipo_date available, use that; else use earliest
            if start_date is not None and start_date != "":
                start = pd.to_datetime(start_date)
            elif ipo_date:
                start = pd.to_datetime(ipo_date)
            else:
                start = hist.index.min()

            end = pd.to_datetime(end_date)

            # Filter history
            hist = hist.loc[(hist.index >= start) & (hist.index <= end)]

            if hist.empty:
                st.warning("No historical data available for the chosen range/ticker.")
            else:
                st.write(f"Showing `Close` price for {ticker_input} from {start.date()} to {end.date()}")
                st.line_chart(hist['Close'])
                st.dataframe(hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10))

        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
else:
    st.info(f"Enter a ticker (default: {default_ticker}) and click 'Fetch and plot' in the sidebar.")
