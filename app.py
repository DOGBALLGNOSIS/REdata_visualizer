from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly
import json
import requests
import pandas as pd
import os
from matplotlib.colors import to_rgb, to_hex
import random

app = Flask(__name__)

# Define the path to the CSV file relative to the main directory
csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'median_home_prices.csv')

# Load data from CSV
data = pd.read_csv(csv_file_path)
data.columns = ['County'] + [str(year) for year in range(2015, 2025)]  # Update the range to include 2023 and 2024

# List of available counties for search
available_counties = data['County'].tolist()

# Function to lighten the color
def lighten_color(color, amount=0.5):
    try:
        c = to_rgb(color)
    except ValueError:
        c = to_rgb('#' + color)
    c = [(1 - (1 - x) * (1 - amount)) for x in c]
    return to_hex(c)

# Function to generate a random color
def random_color():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

# Dictionary to store colors for each county
county_colors = {}

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
    show_predictions = request.args.get('show_predictions', 'false') == 'true'  # Default to false
    fig = go.Figure()

    for county in counties:
        # Assign a consistent color for each county
        if county not in county_colors:
            county_colors[county] = random_color()
        color = county_colors[county]
        trace_name = county

        # Get historical data for the county
        county_data = data[data['County'] == county]
        if county_data.empty:
            print(f"No data found for county: {county}")
            continue
        county_data = county_data.iloc[0]
        years = data.columns[1:].tolist()
        prices = county_data[1:].tolist()

        # Add historical data to the plot
        fig.add_trace(go.Scatter(x=years, y=prices, mode='lines+markers', name=trace_name, line=dict(color=color, shape='spline', smoothing=1.3)))

        if show_predictions:
            try:
                # Fetch predicted data from the polynomial regression microservice
                print(f"Requesting predictions for county: {county}")
                response = requests.post('http://127.0.0.1:5001/predict', json={'county': county})
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                predicted_data = response.json()

                # Log the predicted data
                print(f"Predicted data for {county}: {predicted_data}")

                # Ensure prediction data matches format
                future_years = list(map(str, predicted_data.keys()))
                future_prices = list(predicted_data.values())

                # Lighten the color for the prediction trace
                lighter_color = lighten_color(color, amount=0.5)

                # Add the dotted line connecting the last historical point to the first predicted point
                fig.add_trace(go.Scatter(x=[years[-1], future_years[0]], y=[prices[-1], future_prices[0]], mode='lines', name=trace_name + " (Transition)", line=dict(dash='dot', color=color)))

                # Add predicted data to the plot
                fig.add_trace(go.Scatter(x=future_years, y=future_prices, mode='lines+markers', name=trace_name + " (Predicted)", line=dict(dash='dot', color=lighter_color, shape='spline', smoothing=1.3)))
            except requests.exceptions.RequestException as e:
                print(f"Prediction service error for county {county}: {e}")
                continue

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print("Graph JSON:", graphJSON)  # Debug log
    return graphJSON

if __name__ == '__main__':
    app.run(debug=True)
