from flask import Flask, render_template, request
import yfinance as yf

application = Flask(__name__)

@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_code = request.form['stock_code'].upper()  # Convert to uppercase to handle case sensitivity
        days_past = int(request.form['days_past'])
        return predict_next_day_price_with_sma_optimized(stock_code, days_past)
    return render_template('index.html')

def predict_next_day_price_with_sma_optimized(stock_code, days_past):
    # Ensure days_past is within the allowed range [5, 30]
    days_past = max(5, min(days_past, 30))
    
    # Calculate the minimum period to fetch based on the weekends and potential holidays
    fetch_days = int(days_past * 1.5)
    
    # Fetch stock data
    stock = yf.Ticker(stock_code)
    
    # Retrieve the historical market data for the calculated period
    hist = stock.history(period=f"{fetch_days}d")

    # Check if we have enough data to compute the SMA
    if len(hist) < days_past:
        error_message = "Not enough data available to calculate the SMA for the requested period."
        return render_template('results.html', error=error_message)
    
    # Calculate the SMA for the specified window
    hist['SMA'] = hist['Close'].rolling(window=days_past).mean()
    prediction = hist['SMA'].iloc[-1]
    # Pass the last 'days_past' days of closing prices, the SMA and the prediction to the results page
    return render_template('results.html', history=hist[['Close', 'SMA']].tail(days_past).to_dict(orient='records'), prediction=prediction, stock_code=stock_code)

if __name__ == '__main__':
    application.run(debug=True)
