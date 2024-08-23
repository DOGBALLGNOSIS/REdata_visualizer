from flask import Flask, request, jsonify
import pandas as pd
import geopandas as gpd
import os
import folium

app = Flask(__name__)

# Path to the CSV and GeoJSON files
csv_file_path = r"C:\zillow_visualizer\data\median_home_prices.csv"
geojson_file_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"

# Load data from CSV
data = pd.read_csv(csv_file_path)
data.columns = ['County'] + [str(year) for year in range(2015, 2025)]

# Load GeoJSON data (manually pre-parsed for WA data currently)
geo_df = gpd.read_file(geojson_file_path)

@app.route('/prepare_heatmap_data', methods=['POST'])
def prepare_heatmap_data():
    try:
        year = request.json.get('year', '2024')

        # Prepare the data for the selected year
        data['County'] = data['County'].str.lower().str.replace(" ", "")
        geo_df['NAME'] = geo_df['NAME'].str.lower().str.replace(" ", "")
        merged = geo_df.set_index('NAME').join(data.set_index('County'), how='inner', lsuffix='_geo', rsuffix='_data')
        merged = merged.dropna(subset=[year])

        if merged.empty:
            return jsonify({"error": "No valid data to plot."}), 404

        min_val = merged[year].min()
        max_val = merged[year].max()

        response = {
            'data': merged.to_json(),
            'min_val': min_val,
            'max_val': max_val
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5004, debug=True)
