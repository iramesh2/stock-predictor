from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
import numpy as np
from predictive_methods import monte_carlo_simulation

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    stock_code = request.form['stock_code'].upper()
    days_past = int(request.form['days_past'])
    stock = yf.Ticker(stock_code)
    hist = stock.history(period=f"{days_past}d")
    hist.reset_index(inplace=True)
    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
    hist = hist[['Date', 'Close']].to_dict(orient='records')
    return jsonify(hist)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        json_data = request.get_json()
        days_past = int(json_data['days_past'])
        prediction_model = json_data['prediction_model']
        data = json_data['data']
        
        df = pd.DataFrame(data)
        prediction = None
        model_used = None

        if prediction_model == 'sma':
            df['SMA'] = df['Close'].rolling(window=days_past).mean()
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
            returns = df['Close'].pct_change().dropna()
            mu = np.mean(returns)
            sigma = np.std(returns)
            mean_end_price, _ = monte_carlo_simulation(df['Close'].iloc[-1], days_past, mu, sigma, 1000)
            prediction = mean_end_price
            model_used = 'Monte Carlo Simulation'

        # Instead of returning a template, return JSON data as the frontend expects it.
        return jsonify({
            'prediction': prediction,
            'model_used': model_used
        })
        
    except KeyError as e:
        return jsonify({'error': f'Missing form field: {e}'}), 400
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
