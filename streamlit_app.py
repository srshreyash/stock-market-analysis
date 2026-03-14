import streamlit as st
import yfinance as yf 
import pandas as pd   

def load_data():
    # Replace with your actual filename
    return pd.read_csv("all_tickers.csv")

df = load_data()

st.set_page_config(layout='wide')

stock_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK-B', 'JPM', 'V']
EXCHANGES = {
    "United States (NYSE/NASDAQ)": ".US",
    "London Stock Exchange": ".L",
    "National Stock Exchange (India)": ".NS",
    # "Toronto Stock Exchange": ".TO",
    # "Australian Securities Exchange": ".AX"
}
selected_exchange = st.sidebar.selectbox('Select Exchange', list(EXCHANGES.keys()))
selected_suffix = EXCHANGES[selected_exchange]

filtered_df = df[df['suffix'].isin([selected_suffix])]
ticker_options = filtered_df['symbol'].tolist()
name_map = dict(zip(filtered_df['symbol'], filtered_df['name']))

selected_ticker = st.sidebar.selectbox(f"Search and select a stock in {selected_exchange}",
    options=ticker_options,
    format_func=lambda x: f"{x} - {name_map.get(x, '')}")

if selected_ticker:
    st.success(f"You selected: **{selected_ticker}** ({name_map.get(selected_ticker)})")

@st.cache_data
def get_stock_data(ticker):
    data = yf.download(ticker, period='1y')
    return data

if selected_ticker:
    st.subheader(f'Historical Data for {selected_ticker}')
    stock_data = get_stock_data(selected_ticker) 
    if not stock_data.empty:
        st.write(stock_data.tail())
    else:
        st.write("No data found for the selected ticker.")

st.subheader(f'Stock Price History for {selected_ticker}')
# stock_data = stock_data.reset_index() 
stock_data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in stock_data.columns]
stock_data.columns = stock_data.columns.str.replace('.', '', regex=False)
df_filtered = stock_data.filter(like='Close')
st.line_chart(df_filtered)

all_stock_data = {}
mag7_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']

for ticker_symbol in mag7_tickers:
    print(f"Fetching data for {ticker_symbol}...")
    data = yf.download(ticker_symbol, period='1y')
    if not data.empty:
        # Extract 'Close' column and directly assign its name
        close_prices = data['Close']
        close_prices.name = ticker_symbol
        all_stock_data[ticker_symbol] = close_prices
    else:
        print(f"No data found for {ticker_symbol}.")

# Combine all 'Close' price Series into a single DataFrame
mag7_df = pd.concat(all_stock_data.values(), axis=1)

normalized_mag7_df = mag7_df.div(mag7_df.iloc[0]) * 100
st.line_chart(normalized_mag7_df)

all_stock_data = {}
indian_indices = [ "^NSEI","^NSEBANK", "^CNXIT", "^CNXFMCG", "^CNXAUTO", "^CNXPSUBANK", "^CNXPHARMA","^CNXREALTY","^CNXMETAL"]

for ticker_symbol in indian_indices:
    print(f"Fetching data for {ticker_symbol}...")
    data = yf.download(ticker_symbol, period='1y')
    if not data.empty:
        # Extract 'Close' column and directly assign its name
        close_prices = data['Close']
        close_prices.name = ticker_symbol
        all_stock_data[ticker_symbol] = close_prices
    else:
        print(f"No data found for {ticker_symbol}.")

# Combine all 'Close' price Series into a single DataFrame
indian_indices_df = pd.concat(all_stock_data.values(), axis=1)

normalized_indian_indices_df = indian_indices_df.div(indian_indices_df.iloc[0]) * 100
st.line_chart(normalized_indian_indices_df)