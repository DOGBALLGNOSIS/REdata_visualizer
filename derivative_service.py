from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'median_home_prices.csv')

@app.route('/calculate_derivative', methods=['POST'])
def calculate_derivative():
    try:
        # Load the data
        data = pd.read_csv(csv_file_path)
        county = request.json.get('county').lower()  # Convert to lowercase

        # Check if the county exists in the data
        if county not in data['County'].str.lower().values:  # Compare in lowercase
            return jsonify({'error': 'County not found'}), 404
        
        # Filter the data for the selected county
        county_data = data[data['County'].str.lower() == county].drop(columns=['County'])
        years = np.array(county_data.columns, dtype=int)
        prices = county_data.values.flatten()

        # Calculate the derivative (yearly change)
        derivatives = np.diff(prices)

        # Prepare and format response for all years
        response = {str(years[i+1]): float(derivatives[i]) for i in range(len(derivatives))}
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5002, debug=True)
