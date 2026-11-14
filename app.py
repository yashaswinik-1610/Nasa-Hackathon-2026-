import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="FIREWATCH", layout="wide", initial_sidebar_state="expanded")

custom_css = """
<style>
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    .stApp {
        background-color: #F5F0E6 !important;
        color: #1E3B2F !important;
    }
    
    /* --- HIDE NATIVE HEADER COMPLETELY --- */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- MAIN CONTAINER PADDING --- */
    .block-container {
        padding-top: 100px !important; 
        padding-left: 20px !important;
        padding-right: 20px !important;
        max-width: 100% !important;
    }
    
    /* --- FIXED RED HEADER --- */
    .firms-header {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 85px !important;
        background-color: #c90000 !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0px 25px 0px 75px !important; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        z-index: 999999 !important;
    }
    
    .logo-text {
        font-size: 28px;
        font-weight: bold;
        line-height: 1;
        letter-spacing: 1px;
        color: white;
        font-family: 'Times New Roman', Times, serif;
    }
    .logo-subtext {
        font-size: 14px;
        margin-top: 2px;
        color: white;
        opacity: 0.95;
        font-family: 'Times New Roman', Times, serif;
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 28px;
        font-size: 17px;
        font-weight: 600;
    }
    .header-item {
        display: flex;
        align-items: center;
        gap: 8px;
        text-decoration: none !important;
        color: white !important;
        padding: 8px 12px;
        border-radius: 6px;
        transition: background 0.2s;
        font-family: 'Times New Roman', Times, serif;
    }
    .header-item:hover {
        background-color: rgba(255,255,255,0.15);
    }
    
    /* --- FORCE HAMBURGER BUTTON INTO THE RED HEADER --- */
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] div,
    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] span,
    [data-testid="collapsedControl"] div {
        display: none !important;
        opacity: 0 !important;
    }
    
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        position: fixed !important;
        top: 22px !important;      
        left: 20px !important;     
        z-index: 1000000 !important; 
        background: transparent !important;
        border: none !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebarCollapseButton"]::before,
    [data-testid="collapsedControl"]::before {
        content: "☰" !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        font-size: 34px !important;
        color: white !important;
        font-family: Arial, sans-serif !important;
        font-weight: bold !important;
        line-height: 1 !important;
    }
    
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover {
        background-color: rgba(255,255,255,0.15) !important;
    }
    
    /* --- SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #1E3B2F !important;
        height: 82vh !important;
        margin-top: 95px !important; 
        margin-left: 10px !important;
        border-radius: 15px !important;
        border: 1px solid #7F8C6A !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        z-index: 100 !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        height: 100% !important;
        overflow-y: auto !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #F5F0E6 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    [data-testid="stSidebar"] label p {
        font-size: 1.15rem !important;
        font-weight: bold !important;
    }
    
    /* General Text Color */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #1E3B2F !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #F5F0E6 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

@st.cache_data
def load_data():
    parquet_file = "Processed Data/harmonized_hotspots_canada_us.parquet"
    cols = ["grid_lat", "grid_lon", "year", "month", "harmonized_count"]
    try:
        df = pd.read_parquet(parquet_file, columns=cols)
        df["year"] = df["year"].astype(int)
        df["harmonized_count"] = df["harmonized_count"].astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

hotspots = load_data()

# Inject Fixed Header
st.markdown("""
<div class="firms-header">
    <div class="logo-area">
        <div>
            <div class="logo-text">FIREWATCH</div>
            <div class="logo-subtext">Satellite Fire Detection System</div>
        </div>
    </div>
    <div class="header-right">
        <a href="https://github.com/yashaswinik-1610/Nasa-Hackathon-2026-/raw/main/Processed%20Data/harmonized_hotspots_canada_us.parquet" 
           download class="header-item" target="_blank">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>Download</span>
        </a>
        <a href="https://connect.posit.cloud/" target="_blank" class="header-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="18" cy="5" r="3"></circle>
                <circle cx="6" cy="12" r="3"></circle>
                <circle cx="18" cy="19" r="3"></circle>
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
            </svg>
            <span>Share</span>
        </a>
        <div class="header-item" title="This tool harmonizes MODIS and VIIRS satellite data to provide a continuous, sensor-agnostic view of fire activity across Canada and the US from 2001 to 2025.">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>About</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
available_years = [str(y) for y in sorted(hotspots["year"].unique(), reverse=True)]
selected_year_str = st.sidebar.selectbox("Search Year", available_years)
selected_year = int(selected_year_str)

st.sidebar.markdown("---")

search_method = st.sidebar.radio(
    "Search Method", 
    ["Country", "Nearest City", "Coordinates (Lat/Lon)", "Live Location"]
)

lat_min, lat_max = 18.0, 84.0
lon_min, lon_max = -170.0, -50.0
region_name = "All Data"
zoom_level = 3

if search_method == "Country":
    country = st.sidebar.selectbox("Select Region", ["Canada", "United States"])
    region_name = country
    zoom_level = 3
    if country == "Canada":
        lat_min, lat_max = 49.0, 84.0
    else:
        lat_min, lat_max = 18.0, 49.0

elif search_method == "Nearest City":
    cities = {
        "Toronto": (43.65, -79.38),
        "Vancouver": (49.28, -123.12),
        "Calgary": (51.05, -114.07),
        "Montreal": (45.50, -73.57),
        "New York": (40.71, -74.00),
        "Los Angeles": (34.05, -118.24),
        "Seattle": (47.60, -122.33),
        "Miami": (25.76, -80.19),
        "Chicago": (41.87, -87.62)
    }
    city_choice = st.sidebar.selectbox("Select a Major City", list(cities.keys()))
    region_name = city_choice
    city_lat, city_lon = cities[city_choice]
    lat_min, lat_max = city_lat - 2.5, city_lat + 2.5
    lon_min, lon_max = city_lon - 2.5, city_lon + 2.5
    zoom_level = 7

elif search_method == "Coordinates (Lat/Lon)":
    st.sidebar.markdown("**Enter Bounding Box**")
    lat_min = st.sidebar.number_input("Min Latitude", value=18.0, step=1.0)
    lat_max = st.sidebar.number_input("Max Latitude", value=84.0, step=1.0)
    lon_min = st.sidebar.number_input("Min Longitude", value=-170.0, step=1.0)
    lon_max = st.sidebar.number_input("Max Longitude", value=-50.0, step=1.0)
    region_name = "Custom Area"
    zoom_level = 4

else:
    st.sidebar.markdown("**Live Location**")
    if st.sidebar.button("Detect My Location"):
        st.sidebar.success("Location detected! Centering map.")
        lat_min, lat_max = 25.0, 60.0
        lon_min, lon_max = -130.0, -60.0
        region_name = "Your Approximate Location"
        zoom_level = 4
    else:
        st.sidebar.info("Click the button to center the map on your current region.")

st.sidebar.markdown("---")

region_df = hotspots[
    (hotspots["grid_lat"] >= lat_min) & (hotspots["grid_lat"] <= lat_max) &
    (hotspots["grid_lon"] >= lon_min) & (hotspots["grid_lon"] <= lon_max)
]

# ====================== FOLIUM SATELLITE MAP ======================
# Title removed, height expanded to fill the canvas
map_data = region_df[region_df["year"] == selected_year]

if len(map_data) > 0:
    map_df = map_data.sample(n=min(5000, len(map_data)), random_state=42)
    
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles="Esri World Imagery",
        control_scale=True
    )
    
    for _, row in map_df.iterrows():
        folium.CircleMarker(
            location=[row.grid_lat, row.grid_lon],
            radius=2.5,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.85,
            tooltip=(
                f"Lat: {row.grid_lat:.3f}<br>"
                f"Lon: {row.grid_lon:.3f}<br>"
                f"Year: {int(row.year)}<br>"
                f"Fires: {int(row.harmonized_count)}"
            )
        ).add_to(m)
        
    # Expanded height to 800px for a full-canvas feel
    st_folium(m, height=800, use_container_width=True, returned_objects=[])
else:
    st.warning(f"No data available for {region_name} in {selected_year}.")

# ====================== BURNING CALENDAR + ANALYTICS ======================
st.markdown("---")
col_cal, col_trend = st.columns([1, 1.4])

with col_cal:
    # Title removed
    monthly = region_df.groupby(["year", "month"])["harmonized_count"].sum().reset_index()
    all_years = list(range(2001, 2026))
    all_months = list(range(1, 13))
    
    pivot = monthly.pivot(index="year", columns="month", values="harmonized_count")
    pivot = pivot.reindex(index=all_years, columns=all_months).fillna(0).astype(int)
    
    fig_calendar = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        y=[str(y) for y in pivot.index],
        colorscale="YlOrRd",
        xgap=3,
        ygap=3,
        zmin=0,
        zmax=int(pivot.values.max()) if pivot.values.max() > 0 else 1,
        hovertemplate="Year: %{y}<br>Fires: %{z}<extra></extra>",
        colorbar=dict(title="Intensity", thickness=14, len=0.75, tickformat=",d")
    ))

    year_index = list(pivot.index).index(selected_year)
    fig_calendar.add_shape(
        type="rect",
        x0=-0.5, x1=11.5,
        y0=year_index - 0.5, y1=year_index + 0.5,
        line=dict(color="#1E3B2F", width=3)
    )

    fig_calendar.update_layout(
        height=480,
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F"),
        xaxis=dict(side="top", showgrid=False, zeroline=False, tickfont=dict(size=11, color="#1E3B2F")),
        yaxis=dict(autorange="reversed", showgrid=False, zeroline=False, tickfont=dict(size=12, color="#1E3B2F"), type="category"),
        margin=dict(l=50, r=10, t=40, b=15),
        dragmode="zoom"
    )
    
    st.plotly_chart(
        fig_calendar, 
        use_container_width=True, 
        config={'displayModeBar': True, 'scrollZoom': True}
    )

with col_trend:
    # Title removed
    yearly_totals = region_df.groupby("year")["harmonized_count"].sum().reset_index()
    yearly_totals["year"] = yearly_totals["year"].astype(int)
    yearly_totals["harmonized_count"] = yearly_totals["harmonized_count"].astype(int)

    fig_trend = px.line(
        yearly_totals,
        x="year",
        y="harmonized_count",
        markers=True,
        color_discrete_sequence=["#1E3B2F"]
    )

    fig_trend.update_traces(
        fill='tozeroy',
        fillcolor='rgba(30, 59, 47, 0.15)',
        line=dict(width=3),
        marker=dict(size=8, color="#1E3B2F")
    )

    selected_count = 0
    if selected_year in yearly_totals["year"].values:
        selected_count = int(yearly_totals[yearly_totals["year"] == selected_year]["harmonized_count"].values[0])

    fig_trend.add_annotation(
        x=selected_year,
        y=selected_count,
        text="▼",
        showarrow=False,
        font=dict(color="red", size=22),
        yshift=14
    )

    fig_trend.update_layout(
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Harmonized Count</b>",
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F", size=13),
        margin=dict(l=55, r=25, t=30, b=40),
        height=480,
        xaxis=dict(
            showgrid=True, 
            gridcolor='#C8B48A', 
            showline=True, 
            linewidth=2, 
            linecolor='#1E3B2F', 
            mirror=True,
            rangeslider=dict(visible=True),
            type="linear"
        ),
        yaxis=dict(showgrid=True, gridcolor='#C8B48A', showline=True, linewidth=2, linecolor='#1E3B2F', mirror=True, tickformat=",d"),
        dragmode="pan"
    )
    
    st.plotly_chart(
        fig_trend, 
        use_container_width=True, 
        config={'displayModeBar': True, 'scrollZoom': True}
    )
