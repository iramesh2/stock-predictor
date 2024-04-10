from flask import Flask, render_template, request, jsonify
import logging
import yfinance as yf
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
import numpy as np
from predictive_methods import monte_carlo_simulation

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    stock_code = request.form['stock_code'].upper()
    days_past = int(request.form['days_past'])
    
    # Get historical stock data
    stock = yf.Ticker(stock_code)
    hist = stock.history(period=f"{days_past}d")
    hist.reset_index(inplace=True)
    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
    hist = hist[['Date', 'Close']].to_dict(orient='records')

    # Get additional dashboard data
    dashboard_data = {
        'currentPrice': stock.info.get('regularMarketPrice', 'N/A'),
        'volume': stock.info.get('volume', 'N/A'),
        'marketCap': stock.info.get('marketCap', 'N/A'),
        # Include more data as required
    }

    # Combine both historical and dashboard data in the response
    response = {
        'history': hist,
        'dashboard': dashboard_data,
    }
    return jsonify(response)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        json_data = request.get_json()
        if not json_data:
            raise ValueError("No JSON payload received")
        
        # Debugging: Log the received JSON data
        app.logger.debug("Received JSON data: %s", json_data)
        
        prediction_model = json_data.get('prediction_model')
        if not prediction_model:
            raise ValueError("Missing 'prediction_model' in JSON payload")

        data = json_data.get('data')
        if not data:
            raise ValueError("Missing 'data' in JSON payload")
        
        df = pd.DataFrame(data)
        prediction = None
        model_used = None

        if prediction_model == 'sma':
            dynamic_window_size = max(5, len(df) // 4)
            df['SMA'] = df['Close'].rolling(window=dynamic_window_size).mean()
            prediction = df['SMA'].iloc[-1]
            model_used = 'Simple Moving Average'


        elif prediction_model == 'linear_regression':
            X = np.array(range(len(df))).reshape(-1, 1)
            y = df['Close'].values
            model = LinearRegression()
            model.fit(X, y)
            next_day = np.array([[len(df)]])
            prediction = model.predict(next_day)[0]
            model_used = 'Linear Regression'

            
        elif prediction_model == 'monte_carlo':
            dynamic_days_past = max(30, len(df) // 2)  # Same logic as before
            log_returns = np.log(df['Close'] / df['Close'].shift(1))  # Calculate log returns
            mu = np.mean(log_returns)
            sigma = np.std(log_returns)
            mean_end_price, _ = monte_carlo_simulation(df['Close'].iloc[-1], dynamic_days_past, mu, sigma, 1000)
            prediction = mean_end_price
            model_used = 'Monte Carlo Simulation'


        # Instead of returning a template, return JSON data as the frontend expects it.
        return jsonify({
            'prediction': prediction,
            'model_used': model_used
        })
        
    except Exception as e:
        # Log the error with stack trace
        app.logger.error("Error in prediction: ", exc_info=True)
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)
