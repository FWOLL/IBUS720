import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Stock Price Dashboard",
    page_icon="📈",
    layout="wide"
)

# Helper functions
def get_stock_data(ticker_symbol):
    """Fetch stock data for the given ticker symbol"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        return ticker, info
    except Exception as e:
        st.error(f"Error fetching data for {ticker_symbol}: {e}")
        return None, None

def get_historical_data(ticker, period):
    """Fetch historical stock data for the specified period"""
    try:
        end_date = datetime.now()
        
        if period == "1 Week":
            start_date = end_date - timedelta(days=7)
        elif period == "1 Month":
            start_date = end_date - timedelta(days=30)
        elif period == "6 Months":
            start_date = end_date - timedelta(days=180)
        elif period == "1 Year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 1 month
            
        hist_data = ticker.history(start=start_date, end=end_date)
        return hist_data
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        return None

def format_large_number(num):
    """Format large numbers with K, M, B, T suffixes"""
    if num is None:
        return "N/A"
    
    if num >= 1_000_000_000_000:
        return f"${num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num / 1_000:.2f}K"
    else:
        return f"${num:.2f}"

# Sidebar
with st.sidebar:
    st.title("📊 Stock Dashboard")
    st.markdown("""
    This app allows you to view real-time and historical stock data for companies listed on major exchanges.
    
    ### Instructions:
    1. Enter a valid stock ticker symbol (e.g., AAPL, MSFT, TSLA)
    2. Click the 'Get Stock Data' button
    3. View current stock information and historical price chart
    4. Adjust the time frame using the dropdown menu
    
    Data is fetched using Yahoo Finance API.
    """)
    
    st.markdown("---")
    st.caption("© 2025 Stock Dashboard App")

# Main page
st.title("📈 Stock Price Dashboard")

# User input
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("Enter Stock Ticker Symbol", "AAPL").upper()
with col2:
    st.markdown("###")
    submit_button = st.button("Get Stock Data", type="primary")

# Display stock data when submit button is clicked
if submit_button or ticker_input:
    if not ticker_input:
        st.warning("Please enter a stock ticker symbol.")
    else:
        with st.spinner(f"Fetching data for {ticker_input}..."):
            ticker, info = get_stock_data(ticker_input)
            
            if ticker and info:
                # Display company info
                st.subheader("Company Information")
                company_name = info.get('longName', ticker_input)
                
                # Layout for company info
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {company_name}")
                    if 'sector' in info and info['sector']:
                        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                    if 'industry' in info and info['industry']:
                        st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                    if 'website' in info and info['website']:
                        st.markdown(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
                
                with col2:
                    if 'longBusinessSummary' in info and info['longBusinessSummary']:
                        st.markdown("**Business Summary:**")
                        st.markdown(f"<div style='height: 100px; overflow-y: auto;'>{info.get('longBusinessSummary', 'N/A')}</div>", unsafe_allow_html=True)
                
                # Horizontal line
                st.markdown("---")
                
                # Display key metrics
                st.subheader("Key Stock Metrics")
                
                # Create three columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    current_price = info.get('currentPrice', "N/A")
                    if current_price != "N/A":
                        st.metric(
                            "Current Price", 
                            f"${current_price:.2f}", 
                            f"{((current_price / info.get('previousClose', current_price)) - 1) * 100:.2f}%" if 'previousClose' in info else None
                        )
                    else:
                        st.metric("Current Price", "N/A")
                    
                    st.metric("Previous Close", f"${info.get('previousClose', 0):.2f}" if 'previousClose' in info else "N/A")
                
                with col2:
                    st.metric("Market Cap", format_large_number(info.get('marketCap')))
                    st.metric("Volume", f"{info.get('volume', 0):,}" if 'volume' in info else "N/A")
                
                with col3:
                    st.metric("P/E Ratio", f"{info.get('trailingPE', 0):.2f}" if 'trailingPE' in info and info['trailingPE'] else "N/A")
                    st.metric("52 Week Range", f"${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}" if 'fiftyTwoWeekLow' in info and 'fiftyTwoWeekHigh' in info else "N/A")
                
                # Horizontal line
                st.markdown("---")
                
                # Historical price chart
                st.subheader("Historical Price Chart")
                
                # Time frame selection
                time_periods = ["1 Week", "1 Month", "6 Months", "1 Year"]
                selected_period = st.selectbox("Select Time Frame", time_periods, index=1)
                
                hist_data = get_historical_data(ticker, selected_period)
                
                if hist_data is not None and not hist_data.empty:
                    # Create a price chart using Plotly
                    fig = go.Figure()
                    
                    # Add price line
                    fig.add_trace(
                        go.Scatter(
                            x=hist_data.index, 
                            y=hist_data['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='royalblue', width=2)
                        )
                    )
                    
                    # Update layout
                    fig.update_layout(
                        title=f"{company_name} Stock Price ({selected_period})",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode="x unified",
                        template="plotly_white",
                        height=500
                    )
                    
                    # Add range selector
                    fig.update_xaxes(
                        rangeslider_visible=True,
                        rangeselector=dict(
                            buttons=list([
                                dict(count=7, label="7d", step="day", stepmode="backward"),
                                dict(count=1, label="1m", step="month", stepmode="backward"),
                                dict(count=6, label="6m", step="month", stepmode="backward"),
                                dict(count=1, label="1y", step="year", stepmode="backward"),
                                dict(step="all")
                            ])
                        )
                    )
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display summary statistics
                    st.subheader("Price Statistics")
                    
                    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                    with stats_col1:
                        st.metric("Open", f"${hist_data['Open'].iloc[-1]:.2f}")
                    with stats_col2:
                        st.metric("High", f"${hist_data['High'].iloc[-1]:.2f}")
                    with stats_col3:
                        st.metric("Low", f"${hist_data['Low'].iloc[-1]:.2f}")
                    with stats_col4:
                        st.metric("Close", f"${hist_data['Close'].iloc[-1]:.2f}")
                    
                    # Display historical data table
                    with st.expander("View Historical Data Table"):
                        st.dataframe(
                            hist_data[['Open', 'High', 'Low', 'Close', 'Volume']].style.format({
                                'Open': '${:.2f}',
                                'High': '${:.2f}',
                                'Low': '${:.2f}',
                                'Close': '${:.2f}',
                                'Volume': '{:,.0f}'
                            }),
                            use_container_width=True
                        )
                else:
                    st.error(f"No historical data available for {ticker_input} over the selected time period.")
            else:
                st.error(f"Could not find stock data for ticker '{ticker_input}'. Please check the symbol and try again.")
