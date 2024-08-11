import geopandas as gpd

# LEFTOVER SCRIPT FOR PARSING GEOJSON -- KEEPING IN CASE I SCALE TO NTL DATA LATER
geojson_file_path = r"C:\zillow_visualizer\filtered_washington_counties.geojson"
geo_df = gpd.read_file(geojson_file_path)
geo_df = geo_df[geo_df['STATEFP'] == '53']

print("Filtered GeoJSON structure (first feature):", geo_df.iloc[0].to_dict())
print(f"Total counties in Washington State after filtering: {len(geo_df)}")
