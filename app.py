import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION & CUSTOM CSS
st.set_page_config(page_title="Harmonized Fire Calendar", layout="wide")

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
    
    /* Hide Streamlit default header and footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style all text to be dark green */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #1E3B2F !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #F5F0E6 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 2. LOAD DATA
@st.cache_data
def load_data():
    parquet_file = "Processed Data/harmonized_hotspots_canada_us.parquet"
    cols = ["grid_lat", "grid_lon", "year", "month", "harmonized_count"]
    try:
        return pd.read_parquet(parquet_file, columns=cols)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

hotspots = load_data()

# 3. STRICT TOP HEADER
col_logo, col_spacer, col_share, col_download, col_about = st.columns([4, 5, 1, 1, 1])

with col_logo:
    st.markdown("<h2 style='margin-bottom: 0;'>Harmonized Fire Calendar</h2>", unsafe_allow_html=True)

with col_share:
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("Share", "https://connect.posit.cloud/", use_container_width=True)

with col_download:
    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = hotspots.sample(1000).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download", 
        data=csv_data, 
        file_name="fire_data.csv", 
        mime="text/csv",
        use_container_width=True
    )

with col_about:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.popover("About", use_container_width=True):
        st.write("**About this App**")
        st.write("This tool harmonizes MODIS and VIIRS satellite data to provide a continuous view of fire activity.")

st.markdown("---")

# 4. SIDEBAR LAYOUT
st.sidebar.markdown("<h3 style='text-align: center;'>Filters</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

country = st.sidebar.selectbox("Select Region", ["Canada", "United States"])
selected_year = st.sidebar.slider("Select Year for Map", min_value=2001, max_value=2025, value=2023)

st.sidebar.markdown("---")
show_graph = st.sidebar.toggle("Show Analytics Graph", value=True)
use_bbox = st.sidebar.toggle("Enable Bounding Box Filter")

lat_min, lat_max = 18.0, 84.0
lon_min, lon_max = -170.0, -50.0

if use_bbox:
    st.sidebar.markdown("**Bounding Box Settings**")
    lat_min = st.sidebar.number_input("Min Latitude", value=18.0, step=1.0)
    lat_max = st.sidebar.number_input("Max Latitude", value=84.0, step=1.0)
    lon_min = st.sidebar.number_input("Min Longitude", value=-170.0, step=1.0)
    lon_max = st.sidebar.number_input("Max Longitude", value=-50.0, step=1.0)

# 5. FILTERING LOGIC
if country == "Canada":
    region_df = hotspots[hotspots["grid_lat"] > 49.0]
else:
    region_df = hotspots[hotspots["grid_lat"] <= 49.0]

if use_bbox:
    region_df = region_df[
        (region_df["grid_lat"] >= lat_min) & (region_df["grid_lat"] <= lat_max) &
        (region_df["grid_lon"] >= lon_min) & (region_df["grid_lon"] <= lon_max)
    ]

# 6. MAIN DASHBOARD LAYOUT
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("<h3 style='text-align: center;'>Map</h3>", unsafe_allow_html=True)
    map_data = region_df[region_df["year"] == selected_year]
    
    if len(map_data) > 0:
        # Sample to keep it fast
        map_df = map_data.sample(n=min(5000, len(map_data)), random_state=42)
        
        # --- FOLIUM SATELLITE MAP ---
        # Using Esri World Imagery for the realistic satellite look
        m = folium.Map(location=[45, -100], zoom_start=3, tiles="Esri World Imagery")
        
        # Add bright red dots
        for _, row in map_df.iterrows():
            folium.CircleMarker(
                location=[row.grid_lat, row.grid_lon],
                radius=2, 
                color="red",
                fill=True, 
                fill_color="red",  
                fill_opacity=0.8,
                tooltip=f"Lat: {row.grid_lat:.3f}<br>Lon: {row.grid_lon:.3f}<br>Year: {row.year}<br>Fires: {row.harmonized_count}"
            ).add_to(m)
            
        # Display the map
        st_folium(m, height=550, use_container_width=True)
    else:
        st.warning(f"No data available for {country} in {selected_year}.")

with col2:
    st.markdown("<h3 style='text-align: center;'>Burning Calendar</h3>", unsafe_allow_html=True)
    
    monthly = region_df.groupby(["year", "month"])["harmonized_count"].sum().reset_index()
    monthly["year_str"] = monthly["year"].astype(str)
    
    # GitHub-style scatter squares
    fig_calendar = px.scatter(
        monthly,
        x="month",
        y="year_str",
        color="harmonized_count",
        color_continuous_scale="YlOrRd",
        size=[1] * len(monthly),
        size_max=15
    )
    
    fig_calendar.update_traces(
        marker=dict(
            symbol="square", 
            size=12, 
            line=dict(width=1, color='#F5F0E6')
        )
    )

    fig_calendar.add_shape(
        type="rect", 
        x0=0.5, x1=12.5, 
        y0=str(selected_year), y1=str(selected_year), 
        line=dict(color="#1E3B2F", width=3)
    )

    fig_calendar.update_layout(
        height=550,
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F"),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            side="top",
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            categoryorder="category descending",
            showgrid=False,
            zeroline=False,
            title="Year"
        ),
        margin=dict(l=50, r=10, t=40, b=20)
    )
    st.plotly_chart(fig_calendar, use_container_width=True)

# 7. ANALYTICS GRAPH
if show_graph:
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Yearly Fire Trend</h3>", unsafe_allow_html=True)
    yearly_totals = region_df.groupby("year")["harmonized_count"].sum().reset_index()

    # Thick filled area chart
    fig_trend = px.area(
        yearly_totals, 
        x="year", 
        y="harmonized_count", 
        color_discrete_sequence=["#1E3B2F"] 
    )

    fig_trend.update_traces(
        line=dict(width=4),
        fillcolor="rgba(30, 59, 47, 0.3)"
    )

    fig_trend.update_layout(
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Total Fire Detections</b>",
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F", size=14),
        margin=dict(l=50, r=20, t=30, b=20),
        height=400
    )

    selected_count = yearly_totals[yearly_totals["year"] == selected_year]["harmonized_count"].values[0]
    fig_trend.add_annotation(
        x=selected_year, 
        y=selected_count,
        text="▼", 
        showarrow=False,
        font=dict(color="red", size=24),
        yshift=15
    )

    st.plotly_chart(fig_trend, use_container_width=True)
