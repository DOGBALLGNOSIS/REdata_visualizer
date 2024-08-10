from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import random
import traceback

app = Flask(__name__)

# Define the path to CSV
csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'median_home_prices.csv')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Load data
        data = pd.read_csv(csv_file_path)
        
        # Extract county from request
        county = request.json.get('county')
        if county not in data['County'].values:
            print(f"County not found: {county}")
            return jsonify({'error': 'County not found'}), 404
        
        # Prep data for polynomial regression
        county_data = data[data['County'] == county].drop(columns=['County'])
        years = np.array(county_data.columns, dtype=int).reshape(-1, 1)
        prices = county_data.values.flatten()
        
        #Log the input data for debugging
        print(f"County: {county}")
        print(f"Years: {years.flatten()}")
        print(f"Prices: {prices}")
        
        # Calculate the moving average of the historical prices
        moving_avg = np.convolve(prices, np.ones(3)/3, mode='valid')
        # Append last value and make same length as the original prices
        moving_avg = np.append(moving_avg, [moving_avg[-1]] * (len(prices) - len(moving_avg)))
        
        # Transform for polynomial regression
        poly = PolynomialFeatures(degree=3)
        years_poly = poly.fit_transform(years)
        model = LinearRegression()
        model.fit(years_poly, prices)
        
        # Predict future values for the next 6 years (2025-2030)
        future_years = np.array(range(2025, 2031)).reshape(-1, 1)
        future_years_poly = poly.transform(future_years)
        future_prices = model.predict(future_years_poly)
        
        initial_derivative = np.diff(prices)[-1]
        
        # Apply perturbation towards the moving average
        perturbed_prices = [future_prices[0]]
        current_derivative = initial_derivative
        for i in range(1, len(future_prices)):
            # Apply a strong normalizing force initially and increase perturbation over time
            normalization_factor = 0.3 + (0.2 * (i / (len(future_prices) - 1)))
            perturbation_factor = 0.1 + (0.5 * (i / (len(future_prices) - 1)))
            
            # Calculate the perturbation towards the moving average
            target_value = moving_avg[-1] if len(moving_avg) == len(prices) else moving_avg[len(prices) + i - 1]
            perturbation_towards_avg = (target_value - perturbed_prices[-1]) * normalization_factor
            
            # Apply the perturbation with increased randomness variance
            perturbation = random.uniform(-perturbation_factor, perturbation_factor) * current_derivative
            new_price = perturbed_prices[-1] + current_derivative + perturbation_towards_avg + perturbation
            perturbed_prices.append(new_price)
            current_derivative = new_price - perturbed_prices[-2]
        
        perturbed_prices = np.array(perturbed_prices)
        
        # Log the predictions
        print(f"Future Years: {future_years.flatten()}")
        print(f"Future Prices: {perturbed_prices}")
        
        # Prep and format response
        response = {str(int(year)): float(price) for year, price in zip(future_years.flatten(), perturbed_prices.flatten())}

        return jsonify(response)
    except Exception as e:
        print("An error occurred during prediction:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
