import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="Harmonized Fire Calendar", layout="wide")

# Load data (cached for performance)
@st.cache_data
def load_data():
    hotspots = pd.read_parquet("processed_data/harmonized_hotspots_canada_us.parquet")
    monthly = pd.read_csv("processed_data/harmonized_monthly_summary.csv")
    return hotspots, monthly

try:
    hotspots, monthly = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure the 'processed_data' folder exists with the correct files.")
    st.stop()

# Sidebar configuration
st.sidebar.title("Search and Filters")

view_mode = st.sidebar.radio("View Mode", ["General User", "Admin (Data Export)"])
country = st.sidebar.selectbox("Select Region", ["All (Canada + US)", "Canada", "United States"])

st.sidebar.subheader("Bounding Box")
lat_min = st.sidebar.number_input("Min Latitude", value=18.0, step=1.0)
lat_max = st.sidebar.number_input("Max Latitude", value=84.0, step=1.0)
lon_min = st.sidebar.number_input("Min Longitude", value=-170.0, step=1.0)
lon_max = st.sidebar.number_input("Max Longitude", value=-50.0, step=1.0)

# Filtering logic
if country == "Canada":
    filtered_hotspots = hotspots[hotspots["grid_lat"] > 49.0]
elif country == "United States":
    filtered_hotspots = hotspots[hotspots["grid_lat"] <= 49.0]
else:
    filtered_hotspots = hotspots

filtered_hotspots = filtered_hotspots[
    (filtered_hotspots["grid_lat"] >= lat_min) & (filtered_hotspots["grid_lat"] <= lat_max) &
    (filtered_hotspots["grid_lon"] >= lon_min) & (filtered_hotspots["grid_lon"] <= lon_max)
]

# Admin download button
if view_mode == "Admin (Data Export)":
    st.sidebar.subheader("Export Data")
    csv = filtered_hotspots.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Filtered CSV",
        data=csv,
        file_name="filtered_hotspots.csv",
        mime="text/csv"
    )

# Main dashboard layout
st.title("Harmonized Fire Hotspot Calendar")
st.write(f"Currently viewing: **{country}**")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Hotspot Map")
    
    # Sample data so the browser doesn't crash rendering millions of points
    if len(filtered_hotspots) > 0:
        map_df = filtered_hotspots.sample(n=min(10000, len(filtered_hotspots)), random_state=42)
        
        m = folium.Map(location=[50, -100], zoom_start=3, tiles="CartoDB dark_matter")
        for _, row in map_df.iterrows():
            folium.CircleMarker(
                location=[row.grid_lat, row.grid_lon],
                radius=2,
                color="#ff7800",
                fill=True,
                fill_opacity=0.6,
                popup=f"Lat: {row.grid_lat:.2f}, Lon: {row.grid_lon:.2f} | Count: {row.harmonized_count}"
            ).add_to(m)
            
        st_folium(m, height=500, use_container_width=True)
    else:
        st.warning("No data available for the selected region.")

with col2:
    st.subheader("Burning Calendar")
    pivot_table = monthly.pivot(index="year", columns="month", values="harmonized_count")
    
    fig_calendar = px.imshow(
        pivot_table,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Month", y="Year", color="Fires")
    )
    fig_calendar.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_calendar, use_container_width=True)

# Analytics graph
st.subheader("Yearly Trend Analysis")
yearly_totals = filtered_hotspots.groupby("year")["harmonized_count"].sum().reset_index()

fig_trend = px.line(
    yearly_totals, 
    x="year", 
    y="harmonized_count", 
    markers=True,
    labels={"year": "Year", "harmonized_count": "Total Hotspot Detections"}
)
fig_trend.update_layout(margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_trend, use_container_width=True)
