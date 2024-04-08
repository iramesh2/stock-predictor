from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Display the form to get the stock symbol and number of days
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
    data = json.loads(request.form['data'])
    days_past = int(request.form['days_past'])
    df = pd.DataFrame(data)
    df['SMA'] = df['Close'].rolling(window=days_past).mean()
    prediction = df['SMA'].iloc[-1]
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)
