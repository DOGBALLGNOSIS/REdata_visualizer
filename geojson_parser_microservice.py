import geopandas as gpd

# Paths to the input and output files
input_geojson_path = r"C:\zillow_visualizer\washington_counties.geojson"  # Contains national data
output_geojson_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"

# Load the GeoJSON file
gdf = gpd.read_file(input_geojson_path)

# Filter for only Washington State counties (FIPS code 53)
washington_gdf = gdf[gdf['STATEFP'] == '53']

# Print the names of the counties to verify
print("Filtered counties in Washington State:")
print(washington_gdf['NAME'].unique())

# Save the filtered GeoJSON to a new file
washington_gdf.to_file(output_geojson_path, driver='GeoJSON')

print(f"Filtered GeoJSON file saved to {output_geojson_path}")
