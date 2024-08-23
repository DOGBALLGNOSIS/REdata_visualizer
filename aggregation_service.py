from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'median_home_prices.csv')

@app.route('/aggregate', methods=['POST'])
def aggregate_data():
    try:
        # Load the data
        data = pd.read_csv(csv_file_path)
        county = request.json.get('county').lower()  # Convert to lowercase

        # Check if the county exists in the data
        if county not in data['County'].str.lower().values:
            return jsonify({'error': 'County not found'}), 404
        
        # Filter the data for the selected county
        county_data = data[data['County'].str.lower() == county].drop(columns=['County'])
        
        # Calculate aggregate statistics
        avg_price = county_data.mean(axis=1).values[0]
        median_price = county_data.median(axis=1).values[0]
        std_dev = county_data.std(axis=1).values[0]

        response = {
            'county': county,
            'average_price': avg_price,
            'median_price': median_price,
            'std_dev': std_dev
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5003, debug=True)
