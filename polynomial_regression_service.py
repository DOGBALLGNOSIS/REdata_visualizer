from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np
import os

app = Flask(__name__)

# Define the path to the CSV file relative to the main directory
csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'median_home_prices.csv')

@app.route('/predict', methods=['POST'])
def predict():
    # Load data from CSV
    data = pd.read_csv(csv_file_path)
    
    # Extract county from request
    county = request.json.get('county')
    if county not in data['County'].values:
        return jsonify({'error': 'County not found'}), 404
    
    # Prepare data for polynomial regression
    county_data = data[data['County'] == county].drop(columns=['County'])
    years = np.array(county_data.columns, dtype=int).reshape(-1, 1)
    prices = county_data.values.flatten()
    
    # Transform the data for polynomial regression
    poly = PolynomialFeatures(degree=2)
    years_poly = poly.fit_transform(years)
    
    # Perform polynomial regression
    model = LinearRegression()
    model.fit(years_poly, prices)
    
    # Predict future values for the next 5 years
    future_years = np.array(range(2023, 2028)).reshape(-1, 1)
    future_years_poly = poly.transform(future_years)
    future_prices = model.predict(future_years_poly)
    
    # Prepare response
    response = {year: price for year, price in zip(future_years.flatten(), future_prices.flatten())}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)