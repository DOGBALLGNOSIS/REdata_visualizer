**CS361- Real Estate Data Visualizer**

This project is a microserice-backed web application for visualizing real estate data. 
The application provides interactive plots and heatmaps to show the distribution of median home prices across different states and counties. 
The project includes several microservices for data processing, visualization, and prediction. It is designed to process geojson since I am planning on replacing the polynomial regresison service with a ML regression algo. 

**Features:**

Interactive plots and heatmaps for visualizing median home prices.
![image](https://github.com/user-attachments/assets/14ee5b50-7ee1-497e-a68a-0679b6487726)
![image](https://github.com/user-attachments/assets/daee7d40-ac96-470d-99d4-15b0804c038b)

Integration with Plotly for dynamic and interactive visualizations.
Microservices for data processing, including generating heatmap visuals and predicting future home prices.
REST API for communication between microservices and the main application.
User-friendly interface for searching and filtering data by county and year.
Auto-updating add/remove/toggle selection for specific county searches.
Ability to visualize current 

**Usage:**

To run the application, ensure you have the required libraries installed (flask, plotly, pandas, geopandas, etc.). The microservices all need to be run in parlell for the application to work. 
The application will be available at http://localhost:5000 by default.
To view project documentation, click the link below:
https://docs.google.com/document/d/1A3F6E9WRinJrJdVO2QNCJbSytBZrWkkl/edit?usp=sharing&ouid=106764838670812002776&rtpof=true&sd=true
