from flask import Flask, render_template, request, jsonify
from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import json
from sklearn.linear_model import LinearRegression  # Added for linear regression
import numpy as np  # Often used with scikit-learn for numerical operations


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
    try:
        # Here we assume the incoming data is JSON, so we use request.get_json()
        json_data = request.get_json()
        days_past = int(json_data['days_past'])
        prediction_model = json_data['prediction_model']
        data = json_data['data']  # This is already in the format we need
        
        df = pd.DataFrame(data)
        prediction = None

        if prediction_model == 'sma':
            # Existing logic for Simple Moving Average
            df['SMA'] = df['Close'].rolling(window=days_past).mean()
            prediction = df['SMA'].iloc[-1]
        elif prediction_model == 'linear_regression':
            # Logic for Linear Regression
            # Convert DataFrame index to a 2D array suitable for fitting the model
            X = np.array(range(len(df))).reshape(-1, 1)
            y = df['Close'].values
            
            # Initialize and train the model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict the next closing price using the model
            # The prediction is made for the next day (i.e., the day after the last day in the dataset)
            next_day = np.array([[len(df)]])
            prediction = model.predict(next_day)[0]
            
        return jsonify({'prediction': prediction})
        
    except KeyError as e:
        return jsonify({'error': f'Missing form field: {e}'}), 400
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['POST'])
def results():
    stock_code = request.form['stock_code'].upper()
    # Assume 'data' and 'prediction' are obtained from the form or session after the prediction
    data = request.form['data']  # or session['data'] if you've stored it there
    prediction = request.form['prediction']  # same as above
    prediction_model = request.form['prediction_model']  # retrieved from form or session
    
    # You should have error handling to make sure 'data', 'prediction', and 'prediction_model' are available
    # For example:
    if not data or not prediction or not prediction_model:
        return render_template('error.html', error='Missing data for results.')
    
    # Convert JSON data back to dictionary for template if it's a JSON string
    if isinstance(data, str):
        data = json.loads(data)

    # Render the results page with the prediction data
    return render_template('results.html', stock_code=stock_code, data=data, prediction=prediction, prediction_model=prediction_model)



if __name__ == '__main__':
    app.run(debug=True)
