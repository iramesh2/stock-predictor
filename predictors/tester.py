import yfinance as yf

# Function to retrieve and display stock information
def display_stock_price(ticker_symbol):
    # Fetch stock data
    stock = yf.Ticker(ticker_symbol)
    
    # Retrieve the historical market data
    hist = stock.history(period="5d")  # Example: Get the last 5 days of stock data
    
    # Display stock info
    print(f"Displaying information for: {ticker_symbol}")
    print(hist[['Open', 'High', 'Low', 'Close', 'Volume']])  # Display selected columns

# Example usage
ticker = "AAPL"  # Apple Inc.
display_stock_price(ticker)