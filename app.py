import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION & CUSTOM CSS
st.set_page_config(page_title="FireWatch", layout="wide", initial_sidebar_state="expanded")

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
    
    /* Hide Streamlit default header */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Remove Streamlit's default top padding to make header flush */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    
    /* Style all text to be dark green */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #1E3B2F !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #F5F0E6 !important;
    }
    
    /* --- CUSTOM HEADER CSS --- */
    .firms-header {
        background-color: #c90000;
        padding: 0px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        height: 75px;
        /* Removed shadow and margins to make it blend in */
        width: 100%;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .hamburger {
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
        color: white;
    }
    .logo-area {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-circle {
        width: 45px;
        height: 45px;
        border: 2px solid white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
        color: white;
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
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 30px;
        font-size: 18px;
        font-weight: 600;
    }
    .header-item {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        text-decoration: none;
        color: white;
    }
    .header-item:hover {
        opacity: 0.8;
        color: white;
    }
    
    /* Padding for main content area so it doesn't touch the header */
    .main-content {
        padding: 20px 30px;
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
        df = pd.read_parquet(parquet_file, columns=cols)
        df["year"] = df["year"].astype(int)
        df["harmonized_count"] = df["harmonized_count"].astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

hotspots = load_data()

# 3. INJECT CUSTOM HEADER
st.markdown("""
<div class="firms-header">
    <div class="header-left">
        <div class="hamburger">☰</div>
        <div class="logo-area">
            <div class="logo-circle">NASA</div>
            <div>
                <div class="logo-text">FIREWATCH</div>
                <div class="logo-subtext">Satellite Fire Detection System</div>
            </div>
        </div>
    </div>
    <div class="header-right">
        <a href="https://github.com/yashaswinik-1610/Nasa-Hackathon-2026-/raw/main/Processed%20Data/harmonized_hotspots_canada_us.parquet" download class="header-item">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            <span>Download</span>
        </a>
        <a href="https://connect.posit.cloud/" target="_blank" class="header-item">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
            <span>Share</span>
        </a>
        <div class="header-item" title="This tool harmonizes MODIS and VIIRS satellite data to provide a continuous view of fire activity across Canada and the US from 2001 to 2025.">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            <span>About</span>
        </div>
    </div>
</div>
<div class="main-content">
""", unsafe_allow_html=True)

# 4. SIDEBAR LAYOUT (Search Options)
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
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("<h3 style='text-align: center;'>Map</h3>", unsafe_allow_html=True)
    map_data = region_df[region_df["year"] == selected_year]
    
    if len(map_data) > 0:
        map_df = map_data.sample(n=min(5000, len(map_data)), random_state=42)
        
        m = folium.Map(location=[45, -100], zoom_start=3, tiles="Esri World Imagery")
        
        for _, row in map_df.iterrows():
            folium.CircleMarker(
                location=[row.grid_lat, row.grid_lon],
                radius=2, 
                color="red",
                fill=True, 
                fill_color="red",  
                fill_opacity=0.9,
                tooltip=(
                    f"Lat: {row.grid_lat:.3f}<br>"
                    f"Lon: {row.grid_lon:.3f}<br>"
                    f"Year: {int(row.year)}<br>"
                    f"Fires: {int(row.harmonized_count)}"
                )
            ).add_to(m)
            
        st_folium(m, height=500, use_container_width=True)
    else:
        st.warning(f"No data available for {country} in {selected_year}.")

with col2:
    st.markdown("<h3 style='text-align: center;'>Burning Calendar</h3>", unsafe_allow_html=True)
    
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
        zmax=int(pivot.values.max()),
        hovertemplate="Year: %{y}<br>Fires: %{z}<extra></extra>",
        colorbar=dict(
            title="Intensity", 
            thickness=15, 
            len=0.8,
            x=1.05,
            y=0.5,
            tickformat=",d"
        )
    ))

    year_index = list(pivot.index).index(selected_year)
    fig_calendar.add_shape(
        type="rect", 
        x0=-0.5, x1=11.5, 
        y0=year_index - 0.5, y1=year_index + 0.5, 
        line=dict(color="#1E3B2F", width=3)
    )

    fig_calendar.update_layout(
        height=500,
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F"),
        xaxis=dict(
            side="top",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=12, color="#1E3B2F", weight="bold")
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=13, color="#1E3B2F", weight="bold"),
            title="Year",
            type="category"
        ),
        margin=dict(l=60, r=10, t=50, b=20)
    )
    st.plotly_chart(fig_calendar, use_container_width=True)

# 7. ANALYTICS GRAPH
if show_graph:
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Analytics Graph</h3>", unsafe_allow_html=True)
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

    fig_trend.update_layout(
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Harmonized Count</b>",
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F", size=14),
        margin=dict(l=60, r=30, t=40, b=40),
        height=400,
        xaxis=dict(
            showgrid=True,
            gridcolor='#C8B48A',
            showline=True,
            linewidth=2,
            linecolor='#1E3B2F',
            mirror=True,
            tickfont=dict(color="#1E3B2F", size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#C8B48A',
            showline=True,
            linewidth=2,
            linecolor='#1E3B2F',
            mirror=True,
            tickformat=",d",
            tickfont=dict(color="#1E3B2F", size=12)
        )
    )

    selected_count = int(yearly_totals[yearly_totals["year"] == selected_year]["harmonized_count"].values[0])
    fig_trend.add_annotation(
        x=selected_year, 
        y=selected_count,
        text="▼", 
        showarrow=False,
        font=dict(color="red", size=24),
        yshift=15
    )

    st.plotly_chart(fig_trend, use_container_width=True)

# Close the main-content div
st.markdown("</div>", unsafe_allow_html=True)
