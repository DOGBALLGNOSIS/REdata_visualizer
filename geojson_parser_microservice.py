import geopandas as gpd

# LEFTOVER SCRIPT FOR PARSING GEOJSON -- KEEPING IN CASE I SCALE TO NTL DATA LATER
input_geojson_path = r"C:\zillow_visualizer\washington_counties.geojson"
output_geojson_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"

gdf = gpd.read_file(input_geojson_path)

washington_gdf = gdf[gdf['STATEFP'] == '53']

print("Filtered counties in Washington State:")
print(washington_gdf['NAME'].unique())

washington_gdf.to_file(output_geojson_path, driver='GeoJSON')

print(f"Filtered GeoJSON file saved to {output_geojson_path}")
