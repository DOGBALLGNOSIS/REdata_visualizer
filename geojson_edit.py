import geopandas as gpd

# Load GeoJSON data specifically for Washington State counties
geojson_file_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"

# Load and inspect GeoJSON
geo_df = gpd.read_file(geojson_file_path)

# Filter GeoJSON by Washington State FIPS code (53)
geo_df = geo_df[geo_df['STATEFP'] == '53']

print("Filtered GeoJSON structure (first feature):", geo_df.iloc[0].to_dict())
print(f"Total counties in Washington State after filtering: {len(geo_df)}")
