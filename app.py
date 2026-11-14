import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="FIREWATCH", layout="wide", initial_sidebar_state="expanded")

# ---------- Session state for ordering ----------
if "panel_order" not in st.session_state:
    st.session_state.panel_order = ["calendar", "analytics"]   # default order

custom_css = """
<style>
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    .stApp {
        background-color: #F5F0E6 !important;
        color: #1E3B2F !important;
    }
    
    /* ========== GLASSMORPHISM SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: rgba(30, 59, 47, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        height: 85vh !important;
        margin-top: 85px !important;
        margin-left: 10px !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25) !important;
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
    
    /* Hide original Streamlit icons */
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    button[kind="header"] svg {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Force hamburger button inside the red header */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        position: fixed !important;
        top: 16px !important;
        left: 18px !important;
        z-index: 999999 !important;
        width: 48px !important;
        height: 48px !important;
        background: transparent !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        border-radius: 8px !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebarCollapseButton"]::before,
    [data-testid="collapsedControl"]::before,
    button[kind="header"]::before {
        content: "☰" !important;
        font-size: 30px !important;
        color: white !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        display: block !important;
    }
    
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover,
    button[kind="header"]:hover {
        background-color: rgba(255,255,255,0.18) !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, label {
        color: #1E3B2F !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #F5F0E6 !important;
    }
    
    /* ========== CUSTOM HEADER ========== */
    .firms-header {
        background-color: #c90000;
        padding: 0px 25px 0px 75px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        height: 75px;
        width: 100%;
        margin-top: 0px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        position: relative;
        z-index: 100;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .logo-area {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-text {
        font-size: 26px;
        font-weight: bold;
        line-height: 1;
        letter-spacing: 1px;
        color: white;
    }
    .logo-subtext {
        font-size: 13px;
        margin-top: 2px;
        color: white;
        opacity: 0.95;
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
        padding: 6px 10px;
        border-radius: 6px;
        transition: background 0.2s;
    }
    .header-item:hover {
        background-color: rgba(255,255,255,0.15);
        color: white !important;
    }
    
    .main-content {
        padding: 10px 20px 20px 20px;
    }
    
    /* ========== GLASSMORPHISM PANELS ========== */
    .glass-panel {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        box-shadow: 0 8px 32px rgba(30, 59, 47, 0.12) !important;
        padding: 18px 16px 12px 16px !important;
        margin-bottom: 18px !important;
    }
    
    .glass-panel h3 {
        margin-top: 0 !important;
        margin-bottom: 12px !important;
    }
    
    /* Arrow buttons */
    .arrow-btn {
        background: rgba(30, 59, 47, 0.15) !important;
        border: 1px solid rgba(30, 59, 47, 0.25) !important;
        border-radius: 8px !important;
        color: #1E3B2F !important;
        font-size: 18px !important;
        padding: 2px 10px !important;
        cursor: pointer !important;
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

# Custom Header
st.markdown("""
<div class="firms-header">
    <div class="header-left">
        <div class="logo-area">
            <div>
                <div class="logo-text">FIREWATCH</div>
                <div class="logo-subtext">Satellite Fire Detection System</div>
            </div>
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
<div class="main-content">
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

# ====================== FULL WIDTH MAP ======================
map_data = region_df[region_df["year"] == selected_year]

if len(map_data) > 0:
    with st.spinner("Loading Map..."):
        map_df = map_data.sample(n=min(6000, len(map_data)), random_state=42)
        
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
            
        st_folium(m, height=620, use_container_width=True, returned_objects=[])
else:
    st.warning(f"No data available for {region_name} in {selected_year}.")

# ====================== MOVEABLE GLASS PANELS ======================
st.markdown("---")

# Arrow controls
col_left, col_mid, col_right = st.columns([1, 6, 1])
with col_mid:
    c1, c2, c3 = st.columns([1, 1, 8])
    with c1:
        if st.button("▲", key="move_up", help="Move first panel up"):
            st.session_state.panel_order = st.session_state.panel_order[::-1]
            st.rerun()
    with c2:
        if st.button("▼", key="move_down", help="Move first panel down"):
            st.session_state.panel_order = st.session_state.panel_order[::-1]
            st.rerun()

# Helper function to render calendar
def render_calendar():
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 8px;'>Burning Calendar</h3>", unsafe_allow_html=True)
    
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
        height=460,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Times New Roman", color="#1E3B2F"),
        xaxis=dict(side="top", showgrid=False, zeroline=False, tickfont=dict(size=11, color="#1E3B2F")),
        yaxis=dict(autorange="reversed", showgrid=False, zeroline=False, tickfont=dict(size=12, color="#1E3B2F"), type="category"),
        margin=dict(l=50, r=10, t=40, b=15)
    )
    st.plotly_chart(fig_calendar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Helper function to render analytics
def render_analytics():
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 8px;'>Analytics Graph - {region_name}</h3>", unsafe_allow_html=True)
    
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
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Times New Roman", color="#1E3B2F", size=13),
        margin=dict(l=55, r=25, t=30, b=40),
        height=460,
        xaxis=dict(showgrid=True, gridcolor='rgba(200,180,138,0.4)', showline=True, linewidth=2, linecolor='#1E3B2F', mirror=True),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,180,138,0.4)', showline=True, linewidth=2, linecolor='#1E3B2F', mirror=True, tickformat=",d")
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Render panels according to current order
col1, col2 = st.columns(2)

if st.session_state.panel_order[0] == "calendar":
    with col1:
        render_calendar()
    with col2:
        render_analytics()
else:
    with col1:
        render_analytics()
    with col2:
        render_calendar()

st.markdown("</div>", unsafe_allow_html=True)
