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

csv_file_path = r"C:\zillow_visualizer\data\median_home_prices.csv"
data = pd.read_csv(csv_file_path)
data.columns = ['County'] + [str(year) for year in range(2015, 2025)]
reverse_mapping = {county.lower().replace(" ", ""): county for county in data['County']}

# Load GeoJSON data (manually pre-parsed for WA data currently)
geojson_file_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"
if not os.path.exists(geojson_file_path):
    raise FileNotFoundError(f"The file {geojson_file_path} does not exist. Please ensure the correct GeoJSON file is available.")

geo_df = gpd.read_file(geojson_file_path)

# List of available counties for search
available_counties = data['County'].tolist()

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

county_colors = {}

@app.route('/plot')
def plot():
    counties = request.args.getlist('counties')
    show_predictions = request.args.get('show_predictions', 'false') == 'true'
    show_statewide_average = request.args.get('show_statewide_average', 'true') == 'true'
    year = request.args.get('year', '2024')

    # Initialize county_colors dictionary
    
    fig = go.Figure()

    if show_statewide_average:
        # Calculate and plot the statewide average trendline
        statewide_avg = data.drop(columns=['County']).mean()
        fig.add_trace(go.Scatter(
            x=statewide_avg.index,
            y=statewide_avg.values,
            mode='lines+markers',
            name="Statewide Average",
            line=dict(color='gray', dash='dash')
        ))

    for county in counties:
        transformed_county = county.lower().replace(" ", "")
        original_county = reverse_mapping.get(transformed_county)
        if not original_county:
            continue

        # Check if the county already has a color assigned, if not generate one
        if original_county not in county_colors:
            county_colors[original_county] = random_color()
        color = county_colors[original_county]

        county_data = data[data['County'].str.lower().str.replace(" ", "") == transformed_county].iloc[0]
        years = data.columns[1:].tolist()
        prices = county_data[1:].tolist()

        # Add actual price trace
        fig.add_trace(go.Scatter(
            x=years,
            y=prices,
            mode='lines+markers',
            name=original_county,
            line=dict(color=color, shape='spline', smoothing=1.3)
        ))

        # Only add predictions if show_predictions is true
        if show_predictions:
            try:
                response = requests.post('http://127.0.0.1:5001/predict', json={'county': original_county})
                response.raise_for_status()
                predicted_data = response.json()
                future_years = list(map(str, predicted_data.keys()))
                future_prices = list(predicted_data.values())
                lighter_color = lighten_color(color, amount=0.5)

                # Combine the last actual price with the predicted prices
                all_years = years + future_years
                all_prices = prices + future_prices

                fig.add_trace(go.Scatter(
                    x=all_years,
                    y=all_prices,
                    mode='lines+markers',
                    name=f"{original_county} (Predicted)",
                    line=dict(dash='dot', color=lighter_color, shape='spline', smoothing=1.3)
                ))
            except requests.exceptions.RequestException as e:
                print(f"Prediction service error for county {original_county}: {e}")
                continue

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/heatmap_plot')
def heatmap_plot():
    year = request.args.get('year', '2024')

    response = requests.post('http://127.0.0.1:5004/prepare_heatmap_data', json={'year': year})
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    heatmap_data = response.json()
    m = folium.Map(location=[47.7511, -120.7401], zoom_start=6, tiles=None)
    folium.TileLayer('cartodbpositron', name='Grayscale').add_to(m)
    colormap = folium.LinearColormap(['lightblue', 'darkblue'], vmin=heatmap_data['min_val'], vmax=heatmap_data['max_val'])

    folium.GeoJson(
        heatmap_data['data'],
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

    colormap.caption = f'Median Home Prices in {year}'
    colormap.add_to(m)
    m.save('templates/heatmap.html')
    inject_slider_script('templates/heatmap.html', '/static/slider_control.js')
    return jsonify({"success": True, "year": year})

@app.route('/aggregate', methods=['POST'])
def aggregate():
    county = request.json.get('county')
    if not county:
        return jsonify({'error': 'County not provided'}), 400

    # Call the aggregation service
    try:
        response = requests.post('http://127.0.0.1:5003/aggregate', json={'county': county})
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code

        aggregate_data = response.json()
        return jsonify(aggregate_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/heatmap_derivative_plot')
def heatmap_derivative_plot():
    year = request.args.get('year', '2024')

    # Prepare the data for the selected year
    data['County'] = data['County'].str.lower().str.replace(" ", "")
    geo_df['NAME'] = geo_df['NAME'].str.lower().str.replace(" ", "")
    merged = geo_df.set_index('NAME').join(data.set_index('County'), how='inner', lsuffix='_geo', rsuffix='_data')

    if '2024_data' in merged.columns:
        merged = merged.rename(columns={'2024_data': '2024'})

    print("Merged DataFrame before dropping NaNs:", merged)

    if year in merged.columns:
        merged = merged.dropna(subset=[year])
    else:
        return jsonify({"success": False, "error": f"Year {year} not found in data."})

    derivative_map = {}
    for county in merged.index:
        formatted_county = f"{county.capitalize()} County"
        original_county = reverse_mapping.get(county, county).lower().replace(" ", "")
        print(f"Sending to derivative service: {original_county}")
        response = requests.post('http://127.0.0.1:5002/calculate_derivative', json={'county': original_county})
        if response.status_code == 200:
            derivative_data = response.json()
            derivative_value = derivative_data.get(year, 0)
            derivative_map[formatted_county] = derivative_value
            
            merged.loc[county, f'Derivative_{year}'] = derivative_value  # Add a new column for the derivative
        else:
            print(f"Failed to fetch derivative data for county {original_county}")

    # Print derivative values for debugging
    for county, derivative_value in derivative_map.items():
        print(f"County: {county}, Derivative Value: {derivative_value}")

    if not merged.empty:
        m = folium.Map(location=[47.7511, -120.7401], zoom_start=6, tiles=None)
        folium.TileLayer('cartodbpositron', name='Grayscale').add_to(m)

        if derivative_map:
            min_val = min(derivative_map.values())
            max_val = max(derivative_map.values())
            colormap = folium.LinearColormap(['red', 'blue'], vmin=min_val, vmax=max_val)
            print(f"Color scale - Min: {min_val}, Max: {max_val}")

            folium.GeoJson(
                merged.__geo_interface__,
                style_function=lambda feature: {
                    'fillColor': colormap(derivative_map.get(feature['properties']['NAMELSAD'], 0)) if 'NAMELSAD' in feature['properties'] else 'transparent',
                    'color': 'black',
                    'weight': 0.5,
                    'fillOpacity': 0.7 if 'NAMELSAD' in feature['properties'] else 0,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['NAMELSAD', year, f'Derivative_{year}'],
                    aliases=['County:', 'Price:', 'Derivative:'],
                    localize=True,
                    sticky=True
                )
            ).add_to(m)

            colormap.caption = f'Derivative Values in {year}'
            colormap.add_to(m)
            m.save('templates/heatmap_derivative.html')

            inject_slider_script('templates/heatmap_derivative.html', '/static/slider_control.js')

            return render_template('heatmap_derivative.html', year=year)
        else:
            return jsonify({"success": False, "error": "No derivative values available."})
    else:
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
    with open(html_path, 'w') as file:
        file.write(content)

heatmap_file_path = 'templates/heatmap.html'
slider_script_path = '/static/slider_control.js'
inject_slider_script(heatmap_file_path, slider_script_path)

if __name__ == '__main__':
    app.run(debug=True)


