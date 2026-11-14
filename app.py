import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION & CUSTOM CSS
st.set_page_config(page_title="Fire Analytics", layout="wide")

custom_css = """
<style>
    /* Hide default Streamlit header and sidebar toggle text */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none !important;}
    
    /* Font family */
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    /* Main background and text color */
    .stApp {
        background-color: #F5F0E6 !important;
        color: #1E3B2F !important;
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1E3B2F !important;
    }
    
    /* Sidebar text color */
    [data-testid="stSidebar"] * {
        color: #F5F0E6 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    /* Make Expander Background Transparent */
    [data-testid="stExpander"] {
        background-color: transparent !important;
        border: 1px solid #7F8C6A !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. LOAD DATA
@st.cache_data
def load_data():
    parquet_file = "Processed Data/harmonized_hotspots_canada_us.parquet"
    try:
        hotspots = pd.read_parquet(parquet_file)
        return hotspots
    except Exception as e:
        st.error(f"Error loading data. Details: {e}")
        st.stop()

hotspots = load_data()

# 3. SIDEBAR LAYOUT
st.sidebar.markdown("<h2 style='text-align: center;'>Fire Analytics</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Country Selection
country = st.sidebar.selectbox("Select Region", ["Canada", "United States"])

# Year Selection (Crucial for map speed)
selected_year = st.sidebar.slider("Select Year for Map", min_value=2001, max_value=2025, value=2023)

# Bounding Box Toggle
st.sidebar.markdown("---")
use_bbox = st.sidebar.toggle("Enable Bounding Box Filter")

lat_min, lat_max = 18.0, 84.0
lon_min, lon_max = -170.0, -50.0

if use_bbox:
    with st.sidebar.expander("Bounding Box", expanded=True):
        # Side-by-side columns to fix the overlapping issue
        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat_min = st.number_input("Min Lat", value=18.0, step=1.0)
            lat_max = st.number_input("Max Lat", value=84.0, step=1.0)
        with col_lon:
            lon_min = st.number_input("Min Lon", value=-170.0, step=1.0)
            lon_max = st.number_input("Max Lon", value=-50.0, step=1.0)

# About Section
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("This tool harmonizes MODIS and VIIRS satellite data to provide a continuous view of fire activity.")

# 4. FILTERING LOGIC
if country == "Canada":
    region_df = hotspots[hotspots["grid_lat"] > 49.0]
else:
    region_df = hotspots[hotspots["grid_lat"] <= 49.0]

# Apply bounding box if toggled
if use_bbox:
    region_df = region_df[
        (region_df["grid_lat"] >= lat_min) & (region_df["grid_lat"] <= lat_max) &
        (region_df["grid_lon"] >= lon_min) & (region_df["grid_lon"] <= lon_max)
    ]

# 5. MAIN DASHBOARD LAYOUT
col1, col2 = st.columns([2, 1])

with col1:
    # Map Data filtered by selected year
    map_data = region_df[region_df["year"] == selected_year]
    
    if len(map_data) > 0:
        # Sample to 5,000 max just to keep the map smooth
        map_df = map_data.sample(n=min(5000, len(map_data)), random_state=42)
        
        # Using Esri World Imagery for a realistic satellite map
        m = folium.Map(location=[45, -100], zoom_start=3, tiles="Esri World Imagery")
        
        for _, row in map_df.iterrows():
            # Added Latitude and Longitude to the tooltip popup
            folium.CircleMarker(
                location=[row.grid_lat, row.grid_lon],
                radius=3, 
                color="#1E3B2F",       
                fill=True, 
                fill_color="#ff7800",  
                fill_opacity=0.8,
                tooltip=(
                    f"<b>Lat:</b> {row.grid_lat:.3f}<br>"
                    f"<b>Lon:</b> {row.grid_lon:.3f}<br>"
                    f"<b>Year:</b> {row.year}<br>"
                    f"<b>Fires:</b> {row.harmonized_count}"
                )
            ).add_to(m)
            
        st_folium(m, height=500, use_container_width=True)
    else:
        st.warning(f"No data available for {country} in {selected_year}.")

with col2:
    # Recalculate monthly summary ONLY for the selected region
    monthly_region = region_df.groupby(["year", "month"])["harmonized_count"].sum().reset_index()
    pivot_table = monthly_region.pivot(index="year", columns="month", values="harmonized_count").fillna(0)
    
    # Yellow to Red palette only
    fig_calendar = px.imshow(
        pivot_table, 
        aspect="auto", 
        color_continuous_scale="YlOrRd", 
        labels=dict(x="Month", y="Year", color="Fire Intensity")
    )
    
    # Add a red box around the selected year to highlight it
    year_index = list(pivot_table.index).index(selected_year)
    fig_calendar.add_shape(
        type="rect", x0=-0.5, x1=11.5, 
        y0=year_index - 0.5, y1=year_index + 0.5, 
        line=dict(color="red", width=3)
    )

    fig_calendar.update_layout(
        height=500, 
        margin=dict(l=50, r=20, t=20, b=20), # Added margins so labels don't overlap
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F")
    )
    st.plotly_chart(fig_calendar, use_container_width=True)

# Bottom: Analytic Graph (Shows all years)
st.markdown("---")
yearly_totals = region_df.groupby("year")["harmonized_count"].sum().reset_index()

fig_trend = px.line(
    yearly_totals, 
    x="year", 
    y="harmonized_count", 
    markers=True,
    labels={"year": "Year", "harmonized_count": "Total Hotspot Detections"},
    color_discrete_sequence=["#1E3B2F"] 
)

# Add a red arrow pointing down at the selected year
selected_count = yearly_totals[yearly_totals["year"] == selected_year]["harmonized_count"].values[0]
fig_trend.add_annotation(
    x=selected_year, y=selected_count,
    text="▼", showarrow=False,
    font=dict(color="red", size=20),
    yshift=15
)

fig_trend.update_layout(
    paper_bgcolor="#F5F0E6",
    plot_bgcolor="#F5F0E6",
    font=dict(family="Times New Roman", color="#1E3B2F"),
    margin=dict(l=50, r=20, t=30, b=20)
)
st.plotly_chart(fig_trend, use_container_width=True)
