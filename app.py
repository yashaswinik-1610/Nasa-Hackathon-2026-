import os
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION & CUSTOM CSS (Colors & Fonts)
st.set_page_config(page_title="Fire Hotspot Calendar", layout="wide")

custom_css = """
<style>
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
    
    /* Headers */
    h1, h2, h3 {
        color: #1E3B2F !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #7F8C6A !important;
        color: #F5F0E6 !important;
        border: none;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #C8B48A !important;
        color: #1E3B2F !important;
    }
    
    /* Expander (Pop-up motion) */
    .streamlit-expanderHeader {
        background-color: #7F8C6A !important;
        color: #F5F0E6 !important;
        border-radius: 5px;
    }
    .streamlit-expanderContent {
        background-color: #F5F0E6 !important;
        border: 1px solid #7F8C6A;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. LOAD DATA FROM YOUR GITHUB FOLDER
@st.cache_data
def load_data():
    
    parquet_file = "Processed Data/harmonized_hotspots_canada_us.parquet"
    monthly_file = "Processed Data/harmonized_monthly_summary.csv"
    
    try:
        hotspots = pd.read_parquet(parquet_file)
        monthly = pd.read_csv(monthly_file)
        return hotspots, monthly
    except Exception as e:
        st.error(f"Error loading data. Please check your folder paths. Details: {e}")
        st.stop()

hotspots, monthly = load_data()

# 3. SIDEBAR LAYOUT 
st.sidebar.markdown("<h1 style='text-align: center; font-size: 2em;'>Fire Analytics</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# View Mode Toggle
view_mode = st.sidebar.radio("Select View Mode", ["Public User", "Admin (Data Export)"])

# Search by Admin
search_query = st.sidebar.text_input("Search by Admin (Filter by Year)")

# Country Name
country = st.sidebar.selectbox("Select Country", ["All (Canada + US)", "Canada", "United States"])

# Latitude & Longitude (Pop-up motion)
with st.sidebar.expander("Latitude & Longitude (Bounding Box)"):
    lat_min = st.number_input("Min Latitude", value=18.0, step=1.0)
    lat_max = st.number_input("Max Latitude", value=84.0, step=1.0)
    lon_min = st.number_input("Min Longitude", value=-170.0, step=1.0)
    lon_max = st.number_input("Max Longitude", value=-50.0, step=1.0)

# Download & Share
if view_mode == "Admin (Data Export)":
    st.sidebar.markdown("### Download & Share")
    csv = hotspots.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Filtered Data (CSV)",
        data=csv,
        file_name="fire_data.csv",
        mime="text/csv"
    )

# About Section
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("This tool harmonizes MODIS and VIIRS satellite data to provide a continuous, sensor-agnostic view of fire activity across Canada and the US from 2001 to 2025.")

# 4. FILTERING LOGIC
if country == "Canada":
    filtered_hotspots = hotspots[hotspots["grid_lat"] > 49.0]
elif country == "United States":
    filtered_hotspots = hotspots[hotspots["grid_lat"] <= 49.0]
else:
    filtered_hotspots = hotspots

# Apply bounding box filter
filtered_hotspots = filtered_hotspots[
    (filtered_hotspots["grid_lat"] >= lat_min) & (filtered_hotspots["grid_lat"] <= lat_max) &
    (filtered_hotspots["grid_lon"] >= lon_min) & (filtered_hotspots["grid_lon"] <= lon_max)
]

# Apply search query (year)
if search_query.isdigit():
    filtered_hotspots = filtered_hotspots[filtered_hotspots["year"] == int(search_query)]

# 5. MAIN DASHBOARD LAYOUT
st.title("Harmonized Fire Hotspot Calendar")
st.write(f"**Currently viewing:** {country}")

# Two columns: Map (Left) & Calendar (Right)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Map")
    if len(filtered_hotspots) > 0:
        # Sample data for smooth performance
        map_df = filtered_hotspots.sample(n=min(10000, len(filtered_hotspots)), random_state=42)
        
        # Using a light map to match your color palette
        m = folium.Map(location=[50, -100], zoom_start=3, tiles="CartoDB positron")
        
        for _, row in map_df.iterrows():
            folium.CircleMarker(
                location=[row.grid_lat, row.grid_lon],
                radius=3, 
                color="#1E3B2F",       # Dark Green
                fill=True, 
                fill_color="#C8B48A",  # Tan/Beige
                fill_opacity=0.8,
                # Pop-up motion effect
                tooltip=f"Year: {row.year}<br>Fires: {row.harmonized_count}"
            ).add_to(m)
            
        st_folium(m, height=500, use_container_width=True)
    else:
        st.warning("No data available for the selected region.")

with col2:
    st.subheader("Burning Calendar")
    pivot_table = monthly.pivot(index="year", columns="month", values="harmonized_count")
    
    # Custom color scale matching your palette
    custom_colorscale = [
        [0.0, "#F5F0E6"],  # Cream
        [0.3, "#C8B48A"],  # Tan
        [0.7, "#7F8C6A"],  # Olive
        [1.0, "#1E3B2F"]   # Dark Green
    ]
    
    fig_calendar = px.imshow(
        pivot_table, 
        aspect="auto", 
        color_continuous_scale=custom_colorscale,
        labels=dict(x="Month", y="Year", color="Fires")
    )
    fig_calendar.update_layout(
        height=500, 
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F")
    )
    st.plotly_chart(fig_calendar, use_container_width=True)

# Bottom: Analytic Graph
st.markdown("---")
st.subheader("Analytic Graph: Yearly Trend")
yearly_totals = filtered_hotspots.groupby("year")["harmonized_count"].sum().reset_index()

fig_trend = px.line(
    yearly_totals, 
    x="year", 
    y="harmonized_count", 
    markers=True,
    labels={"year": "Year", "harmonized_count": "Total Hotspot Detections"},
    color_discrete_sequence=["#1E3B2F"] # Dark Green line
)

fig_trend.update_layout(
    paper_bgcolor="#F5F0E6",
    plot_bgcolor="#F5F0E6",
    font=dict(family="Times New Roman", color="#1E3B2F"),
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig_trend, use_container_width=True)
