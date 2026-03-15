import streamlit as st
import yfinance as yf 
import pandas as pd   
import plotly.graph_objects as go
import streamlit.components.v1 as components

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

stock_data = get_stock_data(selected_ticker)
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
sector_indices = ["NIFTY_PVT_BANK.NS","^CNXINFRA", "^CNXMEDIA", "^CNXSERVICE", "^CNXCMDT","^CNXPSE","^CNXMNC","^CNXENERGY","^NSEI","^NSEBANK", "^CNXIT", "^CNXFMCG", "^CNXAUTO", "^CNXPSUBANK", "^CNXPHARMA","^CNXREALTY","^CNXMETAL"]

sector_indices_df = yf.download(sector_indices, period="10y")['Close'].dropna()
sector_indices_df = sector_indices_df.resample('W-FRI').last()
normalized_sector_indices_df = sector_indices_df.div(sector_indices_df.iloc[0]) * 100

# 2. SORT TICKERS by their last available price (Descending)
# This controls the order in the 'x unified' hover box
last_prices = normalized_sector_indices_df.iloc[-1].sort_values(ascending=False)
sorted_tickers = last_prices.index.tolist()

fig = go.Figure()

for column in sorted_tickers:
    # Calculate % change from the start of the period
    start_price = normalized_sector_indices_df[column].iloc[0]
    current_price = normalized_sector_indices_df[column].iloc[-1]
    pct_change = ((current_price - start_price) / start_price) * 100

    # Clean label name
    display_name = column.replace('^', '')

    if column == "^NSEI":
        line_color = "black"
        line_width = 4  # Thicker for visibility
        display_name = "NIFTY 50 (Benchmark)"
    else:
        line_color = None # Let Plotly choose default colors
        line_width = 2
    
    # Create the label string: "NSEBANK: +2.4%"
    # label_text = f"{display_name}: {pct_change:+.1f}%"

    # Add the line
    fig.add_trace(go.Scatter(
        x=normalized_sector_indices_df.index, 
        y=normalized_sector_indices_df[column], 
        mode='lines', 
        name=display_name,
        line=dict(color=line_color, width=1),
        hovertemplate=f'<b>{display_name}</b>: %{{y:,.1f}}<extra></extra>'
    ))
        
    fig.add_annotation(
        x=normalized_sector_indices_df.index[-1],
        y=current_price,
        text=f"{display_name}: {pct_change:+.1f}%",
        showarrow=False,
        xanchor="left",
        xshift=12, # Push text to the right of the point
        font=dict(size=12 if column == "^NSEI" else 10,
            color=line_color if line_color else "black"),
        bgcolor="rgba(255,255,255,0.8)"
    )

# 3. Clean up layout to make room for labels
fig.update_layout(
    title="Nifty Sectoral Performance vs Benchmark",
    xaxis_title="Date",
    yaxis_title="Closing Price",
    margin=dict(r=200, t=50, b=50), # Increased margin to fit the longer text labels
    hovermode="x",
    xaxis=dict(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dash",
        spikethickness=1,
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        namelength=-1
    ),

    # traceorder="descending" ensures the tooltip follows the visual height of lines
    template="plotly_white",
    height=800,
    width = 2000,
    showlegend=False # Hide legend since we have end-of-line labels
)

# 1. Data Retrieval
nse_indices = [
    "^CNX100", "^CRSLDX", "^NSMIDCP", "^NSEMDCP50", "^CNXSC", "^NSEI"
]

# Cache the data so it doesn't re-download every time you change the dropdown
@st.cache_data
def get_data(tickers):
    df = yf.download(tickers, period="10y")['Close'].dropna(how="all")
    df = df.resample('W-FRI').last()
    return df.div(df.iloc[0]) * 100

normalized_nse_indices_df = get_data(nse_indices)

# 2. Sorting logic
last_prices = normalized_nse_indices_df.iloc[-1].sort_values(ascending=False)
sorted_tickers = last_prices.index.tolist()

# --- STREAMLIT SELECTION UI ---
st.sidebar.header("Chart Controls")

# Checkbox for Select All
select_all = st.sidebar.checkbox("Select All Indices", value=False)

if select_all:
    selected_tickers = sorted_tickers
else:
    # Dropdown (multiselect) for specific indices
    selected_tickers = st.sidebar.multiselect(
        "Choose Indices to Display:",
        options=sorted_tickers,
        default=sorted_tickers[:3] # Starts with top 3 performers
    )

# 3. Build the Figure based on user selection
fig = go.Figure()

for column in selected_tickers:
    # Calculate % change from the start of the period
    start_price = normalized_sector_indices_df[column].iloc[0]
    current_price = normalized_sector_indices_df[column].iloc[-1]
    pct_change = ((current_price - start_price) / start_price) * 100

    # Clean label name
    display_name = column.replace('^', '')

    if column == "^NSEI":
        line_color = "black"
        line_width = 4  # Thicker for visibility
        display_name = "NIFTY 50 (Benchmark)"
    else:
        line_color = None # Let Plotly choose default colors
        line_width = 2
    
    # Create the label string: "NSEBANK: +2.4%"
    # label_text = f"{display_name}: {pct_change:+.1f}%"

    # Add the line
    fig.add_trace(go.Scatter(
        x=normalized_sector_indices_df.index, 
        y=normalized_sector_indices_df[column], 
        mode='lines', 
        name=display_name,
        line=dict(color=line_color, width=1),
        hovertemplate=f'<b>{display_name}</b>: %{{y:,.1f}}<extra></extra>'
    ))
        
    fig.add_annotation(
        x=normalized_sector_indices_df.index[-1],
        y=current_price,
        text=f"{display_name}: {pct_change:+.1f}%",
        showarrow=False,
        xanchor="left",
        xshift=12, # Push text to the right of the point
        font=dict(size=12 if column == "^NSEI" else 10,
            color=line_color if line_color else "black"),
        bgcolor="rgba(255,255,255,0.8)"
    )

# 3. Clean up layout to make room for labels
fig.update_layout(
    title="Nifty Sectoral Performance vs Benchmark",
    xaxis_title="Date",
    yaxis_title="Closing Price",
    margin=dict(r=200, t=50, b=50), # Increased margin to fit the longer text labels
    hovermode="x",
    xaxis=dict(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dash",
        spikethickness=1,
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        namelength=-1
    ),

    # traceorder="descending" ensures the tooltip follows the visual height of lines
    template="plotly_white",
    height=800,
    width = 2000,
    showlegend=False # Hide legend since we have end-of-line labels
)


# 4. Display in Streamlit
# st.title("Nifty Sectoral Performance")
st.plotly_chart(fig, use_container_width=False)

# Comprehensive list of NSE Indices for yfinance
nse_indices = [
    "^CNX100",       # Nifty 100
    "^CRSLDX",       # Nifty 500
    "^NSMIDCP",      # Nifty Next 50
    "^NSEMDCP50",    # Nifty Midcap 50
    "^CNXSC",        # Nifty Smallcap 100
    "^NSEI"
]

nse_indices_df = yf.download(nse_indices, period="10y")['Close'].dropna(how = "all")
nse_indices_df = nse_indices_df.resample('W-FRI').last()
normalized_nse_indices_df = nse_indices_df.div(nse_indices_df.iloc[0]) * 100

# 2. SORT TICKERS by their last available price (Descending)
# This controls the order in the 'x unified' hover box
last_prices = normalized_nse_indices_df.iloc[-1].sort_values(ascending=False)
sorted_tickers = last_prices.index.tolist()

fig = go.Figure()

for column in sorted_tickers:
    # Calculate % change from the start of the period
    start_price = normalized_nse_indices_df[column].iloc[0]
    current_price = normalized_nse_indices_df[column].iloc[-1]
    pct_change = ((current_price - start_price) / start_price) * 100

    # Clean label name
    display_name = column.replace('^', '')

    if column == "^NSEI":
        line_color = "black"
        line_width = 4  # Thicker for visibility
        display_name = "NIFTY 50 (Benchmark)"
    else:
        line_color = None # Let Plotly choose default colors
        line_width = 2
    
    # Create the label string: "NSEBANK: +2.4%"
    # label_text = f"{display_name}: {pct_change:+.1f}%"

    # Add the line
    fig.add_trace(go.Scatter(
        x=normalized_nse_indices_df.index, 
        y=normalized_nse_indices_df[column], 
        mode='lines', 
        name=display_name,
        line=dict(color=line_color, width=1),
        hovertemplate=f'<b>{display_name}</b>: %{{y:,.1f}}<extra></extra>'
    ))
        
    fig.add_annotation(
        x=normalized_nse_indices_df.index[-1],
        y=current_price,
        text=f"{display_name}: {pct_change:+.1f}%",
        showarrow=False,
        xanchor="left",
        xshift=12, # Push text to the right of the point
        font=dict(size=12 if column == "^NSEI" else 10,
            color=line_color if line_color else "black"),
        bgcolor="rgba(255,255,255,0.8)"
    )

# 3. Clean up layout to make room for labels
fig.update_layout(
    title="Nifty Sectoral Performance vs Benchmark",
    xaxis_title="Date",
    yaxis_title="Closing Price",
    margin=dict(r=200, t=50, b=50), # Increased margin to fit the longer text labels
    hovermode="x",
    xaxis=dict(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dash",
        spikethickness=1,
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        namelength=-1
    ),

    # traceorder="descending" ensures the tooltip follows the visual height of lines
    template="plotly_white",
    height=800,
    width = 2000,
    showlegend=False # Hide legend since we have end-of-line labels
)

# 4. Display in Streamlit
# st.title("Nifty Sectoral Performance")
st.plotly_chart(fig, use_container_width=False)

# 1. Define your dictionary for easy mapping
nse_indices_dict = {
    "Nifty 50 (Benchmark)": "^NSEI",
    "Nifty 100 (Large Cap)": "^CNX100",
    "Nifty Next 50": "^NSMIDCP",
    "Nifty 500 (Multicap)": "^CRSLDX",
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Auto": "^CNXAUTO",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty PSU Bank": "^CNXPSUBANK",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Energy": "^CNXENERGY",
    "Nifty Midcap 50": "^NSEMDCP50",
    "Nifty Smallcap 100": "^CNXSC"
}

# 2. Display in a clean, expandable text box
with st.expander("📋 View All Index Tickers (Quick Reference)"):
    st.write("Copy and paste these symbols into your search or configuration:")
    
    # Create a formatted string for a Markdown table
    table_header = "| Index Name | Yahoo Ticker |\n| :--- | :--- |\n"
    table_rows = "\n".join([f"| {name} | `{ticker}` |" for name, ticker in nse_indices_dict.items()])
    
    st.markdown(table_header + table_rows)
    
    # Optional: A code block for easy "Copy All"
    st.code(list(nse_indices_dict.values()), language="python")

# This allows for a full-screen interactive TradingView experience
def tradingview_chart(symbol="NSE:NIFTY"):
    # The official TradingView Widget code
    render_html = f"""
    <div id="tradingview_chart_wrapper" style="height: 600px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "{symbol}",
          "interval": "D",
          "timezone": "Asia/Kolkata",
          "theme": "light",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "hide_side_toolbar": false,  // This enables the drawing tools!
          "allow_symbol_change": true,
          "container_id": "tradingview_chart_wrapper"
        }});
        </script>
    </div>
    """
    components.html(render_html, height=600)

st.title("TradingView in Streamlit")
tradingview_chart("NSE:NIFTY")

