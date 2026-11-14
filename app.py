import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 1. PAGE CONFIG + CUSTOM CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Harmonized Fire Calendar",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    /* Font */
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Main background */
    .stApp {
        background-color: #F5F0E6 !important;
        color: #1E3B2F !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E3B2F !important;
    }
    [data-testid="stSidebar"] * {
        color: #F5F0E6 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Hide default Streamlit header/footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Headings */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #1E3B2F !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #F5F0E6 !important;
    }

    /* Make the sidebar collapse button look like a hamburger (three lines) */
    button[data-testid="stBaseButton-headerNoPadding"] svg path,
    [data-testid="stSidebarCollapsedControl"] svg {
        display: none !important;
    }
    button[data-testid="stBaseButton-headerNoPadding"]::before,
    [data-testid="stSidebarCollapsedControl"]::before {
        content: "☰";
        font-size: 22px;
        color: #1E3B2F;
        font-weight: bold;
        line-height: 1;
    }

    /* Header action buttons styling */
    div[data-testid="stHorizontalBlock"] button,
    div[data-testid="stHorizontalBlock"] a {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. LOAD DATA
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# 3. TOP HEADER (Title + Share / Download / About)
# ─────────────────────────────────────────────
col_title, col_spacer, col_share, col_download, col_about = st.columns([5, 3, 1.1, 1.1, 1.1])

with col_title:
    st.markdown(
        "<h2 style='margin:0; padding-top:6px; color:#1E3B2F;'>Harmonized Fire Calendar</h2>",
        unsafe_allow_html=True
    )

with col_share:
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("↗ Share", "https://connect.posit.cloud/", use_container_width=True)

with col_download:
    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = hotspots.sample(min(5000, len(hotspots))).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download",
        data=csv_data,
        file_name="harmonized_fire_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_about:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.popover("ⓘ About", use_container_width=True):
        st.markdown("**About this App**")
        st.write(
            "This tool harmonizes MODIS and VIIRS satellite data to provide a continuous, "
            "sensor-agnostic view of fire activity across Canada and the US from 2001 to 2025."
        )
        st.caption("Data sources: NASA FIRMS (MODIS + VIIRS)")

st.markdown("---")

# ─────────────────────────────────────────────
# 4. SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.markdown("<h3 style='text-align:center; margin-bottom:0;'>Filters</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

country = st.sidebar.selectbox("Select Region", ["Canada", "United States"])
selected_year = st.sidebar.slider("Select Year for Map", min_value=2001, max_value=2025, value=2023)

st.sidebar.markdown("---")
show_graph = st.sidebar.toggle("Show Yearly Trend", value=True)

use_bbox = st.sidebar.toggle("Enable Bounding Box Filter", value=False)

lat_min, lat_max = 18.0, 84.0
lon_min, lon_max = -170.0, -50.0

if use_bbox:
    st.sidebar.markdown("**Bounding Box**")
    lat_min = st.sidebar.number_input("Min Latitude", value=18.0, step=1.0)
    lat_max = st.sidebar.number_input("Max Latitude", value=84.0, step=1.0)
    lon_min = st.sidebar.number_input("Min Longitude", value=-170.0, step=1.0)
    lon_max = st.sidebar.number_input("Max Longitude", value=-50.0, step=1.0)

# ─────────────────────────────────────────────
# 5. FILTERING
# ─────────────────────────────────────────────
if country == "Canada":
    region_df = hotspots[hotspots["grid_lat"] > 49.0].copy()
else:
    region_df = hotspots[hotspots["grid_lat"] <= 49.0].copy()

if use_bbox:
    region_df = region_df[
        (region_df["grid_lat"] >= lat_min) & (region_df["grid_lat"] <= lat_max) &
        (region_df["grid_lon"] >= lon_min) & (region_df["grid_lon"] <= lon_max)
    ]

# ─────────────────────────────────────────────
# 6. MAIN LAYOUT – Wide Map + GitHub-style Calendar
# ─────────────────────────────────────────────
col_map, col_cal = st.columns([2.2, 1])

# ----- MAP (Version 1 – with map=) -----
with col_map:
    st.markdown("<h3 style='text-align:center; margin-bottom:4px;'>Map</h3>", unsafe_allow_html=True)
    map_data = region_df[region_df["year"] == selected_year]

    if len(map_data) > 0:
        map_df = map_data.sample(n=min(12000, len(map_data)), random_state=42)

        fig_map = px.scatter_map(
            map_df,
            lat="grid_lat",
            lon="grid_lon",
            hover_name="year",
            hover_data={
                "grid_lat": ":.3f",
                "grid_lon": ":.3f",
                "harmonized_count": True,
                "year": False
            },
            color_discrete_sequence=["#ff7800"],
            zoom=3.2,
            center={"lat": 48, "lon": -100},
            map_style="open-street-map",
            height=580
        )
        
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="#F5F0E6",
            map=dict(                   # ← correct property name
                center=dict(lat=48, lon=-100)
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning(f"No data available for {country} in {selected_year}.")

# ----- BURNING CALENDAR (GitHub contribution style) -----
with col_cal:
    st.markdown("<h3 style='text-align:center; margin-bottom:4px;'>Burning Calendar</h3>", unsafe_allow_html=True)

    monthly = region_df.groupby(["year", "month"])["harmonized_count"].sum().reset_index()

    all_years = list(range(2001, 2026))
    all_months = list(range(1, 13))

    pivot = monthly.pivot(index="year", columns="month", values="harmonized_count")
    pivot = pivot.reindex(index=all_years, columns=all_months).fillna(0)

    y_labels = [str(y) for y in pivot.index]
    z_max = float(pivot.values.max()) if pivot.values.max() > 0 else 1

    fig_calendar = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        y=y_labels,
        colorscale=[
            [0.0, "#ebedf0"],
            [0.2, "#c6e48b"],
            [0.4, "#7bc96f"],
            [0.6, "#239a3b"],
            [0.8, "#196127"],
            [1.0, "#0e4429"]
        ],
        xgap=3,
        ygap=3,
        zmin=0,
        zmax=z_max,
        colorbar=dict(
            title=dict(text="Intensity", side="right"),
            thickness=12,
            len=0.75,
            tickfont=dict(size=10)
        ),
        hovertemplate="Year: %{y}<br>Month: %{x}<br>Detections: %{z}<extra></extra>"
    ))

    year_idx = y_labels.index(str(selected_year))
    fig_calendar.add_shape(
        type="rect",
        x0=-0.5, x1=11.5,
        y0=year_idx - 0.5, y1=year_idx + 0.5,
        line=dict(color="#1E3B2F", width=2.5),
        fillcolor="rgba(0,0,0,0)"
    )

    fig_calendar.update_layout(
        height=580,
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F", size=11),
        xaxis=dict(
            side="top",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11),
            fixedrange=True
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10),
            fixedrange=True
        ),
        margin=dict(l=45, r=15, t=35, b=15)
    )
    st.plotly_chart(fig_calendar, use_container_width=True)

# ─────────────────────────────────────────────
# 7. YEARLY FIRE TREND
# ─────────────────────────────────────────────
if show_graph:
    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>Yearly Fire Trend</h3>", unsafe_allow_html=True)

    yearly_totals = (
        region_df.groupby("year")["harmonized_count"]
        .sum()
        .reset_index()
        .sort_values("year")
    )

    fig_trend = px.line(
        yearly_totals,
        x="year",
        y="harmonized_count",
        markers=True,
        color_discrete_sequence=["#1E3B2F"]
    )

    fig_trend.update_traces(
        line=dict(width=3),
        marker=dict(size=9, line=dict(width=1, color="#F5F0E6"))
    )

    sel = yearly_totals[yearly_totals["year"] == selected_year]
    if not sel.empty:
        selected_count = sel["harmonized_count"].values[0]
        fig_trend.add_annotation(
            x=selected_year,
            y=selected_count,
            text="▼",
            showarrow=False,
            font=dict(color="#E63946", size=22),
            yshift=18
        )

    fig_trend.update_layout(
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Total Fire Detections</b>",
        paper_bgcolor="#F5F0E6",
        plot_bgcolor="#F5F0E6",
        font=dict(family="Times New Roman", color="#1E3B2F", size=13),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(30,59,47,0.12)",
            zeroline=False,
            tickmode="linear",
            dtick=2
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(30,59,47,0.12)",
            zeroline=False
        ),
        margin=dict(l=60, r=30, t=20, b=40),
        height=380,
        hovermode="x unified"
    )

    st.plotly_chart(fig_trend, use_container_width=True)
