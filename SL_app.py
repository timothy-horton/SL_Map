import streamlit as st
import folium
from folium import Choropleth
import geopandas as gpd
import pandas as pd
from streamlit_folium import folium_static

# Load the CSV and shapefile
sl_df = pd.read_csv('SL_Doc.csv')  # CSV file with population data
gdf_shapefile = gpd.read_file('sle_admbnda_adm3_gov_ocha_20231215.shp')  # Shapefile

# Clean the columns
sl_df['CHIEFDOM'] = sl_df['CHIEFDOM'].str.strip().str.lower()
gdf_shapefile['ADM3_EN'] = gdf_shapefile['ADM3_EN'].str.strip().str.lower()

# Create a dictionary for faster lookup: CHIEFDOM -> POPULATION
population_dict = dict(zip(sl_df['CHIEFDOM'], sl_df['POPULATION']))

# Function to match population based on ADM3_EN
def get_population_from_csv(chiefdom):
    return population_dict.get(chiefdom, None)

# Apply the function to populate the 'POPULATION' column in the shapefile GeoDataFrame
gdf_shapefile['POPULATION'] = gdf_shapefile['ADM3_EN'].apply(get_population_from_csv)

# Drop unnecessary columns
gdf_shapefile_cleaned = gdf_shapefile.drop(columns=['date', 'validOn', 'validTo'])

# Create a choropleth map using Folium
m = folium.Map(location=[8.0, -11.5], zoom_start=8)

# Add the choropleth layer
folium.Choropleth(
    geo_data=gdf_shapefile_cleaned,
    name="Population by District",
    data=gdf_shapefile_cleaned,
    columns=["ADM3_EN", "POPULATION"],
    key_on="feature.properties.ADM3_EN",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Population by District",
    nan_fill_opacity=0.0,
    bins=5
).add_to(m)

# Add the tooltip for each district
folium.GeoJson(
    gdf_shapefile_cleaned,
    tooltip=folium.GeoJsonTooltip(
        fields=["ADM3_EN", "POPULATION"],
        aliases=["Chiefdom", "Population"],
        sticky=True
    )
).add_to(m)

# Add layer control to toggle the choropleth layer
folium.LayerControl().add_to(m)

# Display the map in Streamlit
folium_static(m)