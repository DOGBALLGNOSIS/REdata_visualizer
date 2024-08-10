from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly
import json
import pandas as pd
import os
import geopandas as gpd
import folium
import random
from matplotlib.colors import to_hex, to_rgb
import requests

app = Flask(__name__)

# Define the path to the CSV file relative to the main directory
csv_file_path = r"C:\zillow_visualizer\data\median_home_prices.csv"

# Load data from CSV
data = pd.read_csv(csv_file_path)
data.columns = ['County'] + [str(year) for year in range(2015, 2025)]

print("CSV Data Loaded:")
print(data.head())

# Create a reverse mapping to restore original county names
reverse_mapping = {county.lower().replace(" ", ""): county for county in data['County']}
print("Reverse mapping created:")
print(reverse_mapping)

# Load GeoJSON data (manually pre-parsed for WA data currently)
geojson_file_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"

# Check if the GeoJSON file exists
if not os.path.exists(geojson_file_path):
    raise FileNotFoundError(f"The file {geojson_file_path} does not exist. Please ensure the correct GeoJSON file is available.")

# Load GeoJSON
geo_df = gpd.read_file(geojson_file_path)
print("GeoJSON structure (first feature):", geo_df.iloc[0].to_dict())

# Small reformattign
geo_df = geo_df.rename(columns={'2024': 'Median_Home_Price_2024'})

print("GeoDataFrame Loaded and Processed:")
print(geo_df[['NAME', 'NAMELSAD']].head())

# List of available counties for search
available_counties = data['County'].tolist()
print("Available counties for search:")
print(available_counties)


def random_color():
    return to_hex([random.random() for _ in range(3)])


def lighten_color(color, amount=0.5):
    c = to_rgb(color)
    c = [(1 - (1 - x) * (1 - amount)) for x in c]
    return to_hex(c)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q').lower()
    results = [county for county in available_counties if query in county.lower()]
    return jsonify(results)

@app.route('/plot')
def plot():
    counties = request.args.getlist('counties')
    show_predictions = request.args.get('show_predictions', 'false') == 'true'
    year = request.args.get('year', '2024')

    print(f"Counties selected for plotting: {counties}")
    print(f"Show predictions: {show_predictions}, Year: {year}")

    # Initialize county_colors dictionary
    county_colors = {}
    fig = go.Figure()

    for county in counties:
        # Fit county name to lowercase for lookup
        transformed_county = county.lower().replace(" ", "")

        # Reverse the transformation to find the correct county name
        if transformed_county in reverse_mapping:
            original_county = reverse_mapping[transformed_county]
        else:
            print(f"No data found for county: {county}")
            continue

        if original_county not in county_colors:
            county_colors[original_county] = random_color()
        color = county_colors[original_county]
        trace_name = original_county

        county_data = data[data['County'].str.lower().str.replace(" ", "") == transformed_county]
        if county_data.empty:
            print(f"No data found for county: {original_county}")
            continue
        county_data = county_data.iloc[0]
        years = data.columns[1:].tolist()
        prices = county_data[1:].tolist()

        print(f"Plotting data for {original_county}:")
        print(f"Years: {years}")
        print(f"Prices: {prices}")

        fig.add_trace(go.Scatter(
            x=years,
            y=prices,
            mode='lines+markers',
            name=trace_name,
            line=dict(color=color, shape='spline', smoothing=1.3)
        ))

        if show_predictions:
            try:
                response = requests.post('http://127.0.0.1:5001/predict', json={'county': original_county})
                response.raise_for_status()
                predicted_data = response.json()

                future_years = list(map(str, predicted_data.keys()))
                future_prices = list(predicted_data.values())
                lighter_color = lighten_color(color, amount=0.5)

                print(f"Predicted data for {original_county}:")
                print(f"Future Years: {future_years}")
                print(f"Future Prices: {future_prices}")

                fig.add_trace(go.Scatter(
                    x=[years[-1], future_years[0]],
                    y=[prices[-1], future_prices[0]],
                    mode='lines',
                    name=trace_name + " (Transition)",
                    line=dict(dash='dot', color=color)
                ))
                fig.add_trace(go.Scatter(
                    x=future_years,
                    y=future_prices,
                    mode='lines+markers',
                    name=trace_name + " (Predicted)",
                    line=dict(dash='dot', color=lighter_color, shape='spline', smoothing=1.3)
                ))
            except requests.exceptions.RequestException as e:
                print(f"Prediction service error for county {original_county}: {e}")
                continue

    # Convert the plotly figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/heatmap_plot')
def heatmap_plot():
    year = request.args.get('year', '2024')

    # Prepare the data for the year selected
    year_data = data[['County', year]].set_index('County')
    print(f"Year Data for Heatmap ({year}):")
    print(year_data.head())

    # Reformat county names in the CSV
    data['County'] = data['County'].str.lower().str.replace(" ", "")
    print("CSV 'County' values after transformation:")
    print(data['County'].unique())

    # Reformat county names in GeoJSON
    geo_df['NAME'] = geo_df['NAME'].str.lower().str.replace(" ", "")
    print("GeoJSON 'NAME' values after transformation:")
    print(geo_df['NAME'].unique())

    # Perform the merge
    merged = geo_df.set_index('NAME').join(data.set_index('County'), how='inner', lsuffix='_geo', rsuffix='_data')
    print(f"Merged DataFrame after join ({year}):")
    print(merged.head())

    # Drop rows with NaN values in the target year column
    merged = merged.dropna(subset=[year])

    print(f"Merged DataFrame after dropping NaNs ({year}):")
    print(merged.head())

    if not merged.empty:
        m = folium.Map(location=[47.7511, -120.7401], zoom_start=6, tiles=None)
        
        # Add the grayscale tiles (STILL WIP)
        folium.TileLayer('cartodbpositron', name='Grayscale').add_to(m)

        # Calculate the color scale dynamically based on the data range for the selected year
        min_val = merged[year].min()
        max_val = merged[year].max()
        colormap = folium.LinearColormap(['lightblue', 'darkblue'], vmin=min_val, vmax=max_val)

        print(f"Color scale - Min: {min_val}, Max: {max_val}")

        # Add GeoJson to the map
        folium.GeoJson(
            merged.__geo_interface__,
            style_function=lambda feature: {
                'fillColor': colormap(feature['properties'][year]) if feature['properties'][year] else 'transparent',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7 if feature['properties'][year] else 0,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NAMELSAD', year],
                aliases=['County:', 'Median Home Price:'],
                localize=True
            )
        ).add_to(m)

        # Add the colormap as a legend
        colormap.caption = f'Median Home Prices in {year}'
        colormap.add_to(m)

        # Save the map to an HTML file for rendering
        m.save('templates/heatmap.html')

        # Inject the slider script
        inject_slider_script('templates/heatmap.html', '/static/slider_control.js')

        return jsonify({"success": True, "year": year})  # Return the selected year with success
    else:
        print(f"Error: No valid data available to plot the heatmap for {year}.")
        return jsonify({"success": False, "error": "No valid data to plot."})

@app.route('/heatmap')
def heatmap():
    year = request.args.get('year', '2024')
    show_heatmap = request.args.get('show_heatmap', 'false') == 'true'
    if show_heatmap:
        return render_template('heatmap.html', year=year)

    return render_template('index.html')


def inject_slider_script(html_path, script_path):
    with open(html_path, 'r') as file:
        content = file.read()
    
    script_tag = f'<script src="{script_path}"></script>'
    
    if '</head>' in content:
        content = content.replace('</head>', f'{script_tag}\n</head>')
    elif '<script' in content:
        last_script_index = content.rfind('<script')
        script_end_index = content.find('>', last_script_index) + 1
        content = content[:script_end_index] + f'\n{script_tag}' + content[script_end_index:]
    else:
        if '</body>' in content:
            content = content.replace('</body>', f'{script_tag}\n</body>')
        else:
            content += f'\n{script_tag}'

    # Write the modified content back to the file
    with open(html_path, 'w') as file:
        file.write(content)

heatmap_file_path = 'templates/heatmap.html'
slider_script_path = '/static/slider_control.js'
inject_slider_script(heatmap_file_path, slider_script_path)

if __name__ == '__main__':
    app.run(debug=True)

