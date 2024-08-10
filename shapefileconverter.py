import geopandas as gpd
import pandas as pd

# Load the county-level shapefile
county_shapefile_path = r"C:\zillow_visualizer\tl_2023_us_county.shp"
geo_df = gpd.read_file(county_shapefile_path)

# Load the CSV file with median home prices
csv_file_path = r"C:\zillow_visualizer\data\median_home_prices.csv"
data = pd.read_csv(csv_file_path)
data.columns = ['County'] + [str(year) for year in range(2015, 2025)]

# Standardize county names in both DataFrames
data['County'] = data['County'].str.replace(r'\s+', '', regex=True).str.lower()
geo_df['NAME'] = geo_df['NAME'].str.replace(r'\s+', '', regex=True).str.lower()

# Handle special cases manually
data['County'] = data['County'].replace({
    'pend': 'pendoreille',  # Adjust the 'pend' name
})
data = data[data['County'] != 'statewide']  # Remove the 'statewide' entry

# Perform the join operation between GeoDataFrame and CSV data
year = '2024'  # Example year
year_data = data[['County', year]].set_index('County')
merged = geo_df.set_index('NAME').join(year_data)

# Check for any NaN values in the merged DataFrame
print(merged.isna().sum())  # Display NaN counts for each column
print(set(data['County']) - set(merged.index))  # Check if any counties are missing after the join

# Optionally save the merged GeoDataFrame to a new GeoJSON file
output_geojson_path = r"C:\zillow_visualizer\washington_counties.geojson"
merged.to_file(output_geojson_path, driver="GeoJSON")

print(f"GeoJSON file saved at {output_geojson_path}")
