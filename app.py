from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)

# Sample data for hardcoding
sample_data = {
    "county1": [100, 110, 115, 120, 130, 140, 150],
    "county2": [90, 95, 100, 105, 110, 115, 120],
    "county3": [80, 85, 90, 95, 100, 105, 110],
    "county4": [120, 125, 130, 135, 140, 145, 150]
}
sample_dates = ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07"]

# List of available counties for search
available_counties = ["County1, State1", "County2, State2", "County3, State3", "County4, State4"]

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
    fig = go.Figure()

    for county in counties:
        data_key = county.split(',')[0].lower()
        data = sample_data.get(data_key, [])
        fig.add_trace(go.Scatter(x=sample_dates, y=data, mode='lines+markers', name=county))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

if __name__ == '__main__':
    app.run(debug=True)