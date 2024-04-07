import yfinance as yf

def predict_next_day_price_with_sma_optimized(stock_code, days_past):
    # Ensure days_past is within the allowed range [5, 30]
    days_past = max(5, min(days_past, 30))
    
    # Calculate the minimum period to fetch based on the weekends and potential holidays
    # Assuming up to two days for weekends plus a conservative estimate for holidays
    fetch_days = int(days_past * 1.5)
    
    # Fetch stock data
    stock = yf.Ticker(stock_code)
    
    # Retrieve the historical market data for the calculated period
    hist = stock.history(period=f"{fetch_days}d")

    # Ensure we have enough data to compute the SMA
    if len(hist) < days_past:
        print("Not enough data available to calculate the SMA for the requested period.")
        return
    
    # Calculate the SMA for the specified window
    hist['SMA'] = hist['Close'].rolling(window=days_past).mean()
    
    # Display the last 'days_past' days of closing prices and SMA
    print(f"Displaying the last {days_past} days of closing prices and SMA for: {stock_code}")
    print(hist[['Close', 'SMA']].tail(days_past))
    
    # Predict the next day's closing price as the SMA of the last 'days_past' days
    prediction = hist['SMA'].iloc[-1]
    print(f"\nPredicted closing price for the next day based on {days_past}-day SMA: {prediction:.2f}")

# Example usage
stock_code = input("Enter the stock code (e.g., 'AAPL' for Apple): ")
days_past = int(input("Enter the number of days in the past to calculate SMA (between 5 and 30): "))
predict_next_day_price_with_sma_optimized(stock_code, days_past)



