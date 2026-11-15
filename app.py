from urllib.parse import quote

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# >>> Put your deployed app link here (used by the Share button) <<<
APP_URL = "https://your-app-name.streamlit.app"
PARQUET = "Processed Data/harmonized_hotspots_canada_us.parquet"

st.set_page_config(page_title="FIREWATCH", layout="wide", initial_sidebar_state="collapsed")

BASE_CSS = """
<style>
html, body, [class*="css"] {font-family:'Times New Roman',Times,serif !important;}
.stApp {background:#F5F0E6 !important;}
.stApp, [data-testid="stAppViewContainer"], section.main {overflow:hidden !important;}
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"],
[data-testid="stElementToolbar"], #MainMenu, footer {display:none !important;}
.block-container {padding:0 !important; max-width:100% !important;}

/* red header */
.firms-header {position:fixed; top:0; left:0; width:100%; height:85px; background:#c90000;
  display:flex; align-items:center; padding:0 25px 0 80px; box-shadow:0 2px 8px rgba(0,0,0,.25); z-index:999999;}
.logo-text {font-size:28px; font-weight:bold; letter-spacing:1px; color:#fff; line-height:1;}
.logo-subtext {font-size:14px; margin-top:2px; color:#fff; opacity:.95;}

/* header buttons (real Streamlit buttons, so they actually work) */
.st-key-menu_btn, .st-key-dl_btn, .st-key-share_btn, .st-key-about_btn {position:fixed; top:20px; z-index:1000001;}
.st-key-menu_btn {left:18px;}
.st-key-about_btn {right:25px;} .st-key-share_btn {right:150px;} .st-key-dl_btn {right:265px;}
.st-key-menu_btn button, .st-key-dl_btn button, .st-key-share_btn button, .st-key-about_btn button {
  background:transparent !important; border:0 !important; box-shadow:none !important; color:#fff !important;}
.st-key-menu_btn button:hover, .st-key-dl_btn button:hover, .st-key-share_btn button:hover, .st-key-about_btn button:hover {
  background:rgba(255,255,255,.18) !important;}
.st-key-menu_btn button p {font:bold 32px Arial !important; color:#fff !important; line-height:1;}
.st-key-dl_btn button p, .st-key-share_btn button p, .st-key-about_btn button p {
  font-size:17px !important; font-weight:600 !important; color:#fff !important;}

/* map fills the whole canvas under the header */
iframe[title="streamlit_folium.st_folium"] {position:fixed !important; top:85px; left:0; width:100vw !important;
  height:calc(100vh - 85px) !important; z-index:1; border:0;}

/* floating filter panel */
.st-key-filters_panel {position:fixed; top:100px; left:14px; width:270px; max-height:calc(100vh - 130px); overflow-y:auto;
  background:#1E3B2F; border:1px solid #7F8C6A; border-radius:15px; padding:14px; z-index:1000; box-shadow:0 4px 12px rgba(0,0,0,.35);}
.st-key-filters_panel *, .st-key-filters_panel label p {color:#F5F0E6 !important;}
.st-key-filters_panel label p {font-size:1.1rem !important; font-weight:bold !important;}

/* glassmorphism chart panel at the bottom */
.st-key-charts_panel {position:fixed; bottom:16px; z-index:1000; padding:6px 16px 10px;
  background:rgba(245,240,230,.50); backdrop-filter:blur(14px) saturate(160%); -webkit-backdrop-filter:blur(14px) saturate(160%);
  border:1px solid rgba(255,255,255,.55); border-radius:18px; box-shadow:0 8px 32px rgba(0,0,0,.35);}
.st-key-charts_panel h5 {text-align:center; margin:0; color:#1E3B2F !important;}
.st-key-charts_btn {display:flex; justify-content:flex-end;}
.st-key-charts_btn button {background:#1E3B2F !important; border:1px solid #7F8C6A !important; border-radius:8px !important; padding:2px 12px !important;}
.st-key-charts_btn button p {color:#F5F0E6 !important; font-weight:bold !important;}
</style>
"""

for key, default in (("show_filters", True), ("show_charts", True)):
    st.session_state.setdefault(key, default)


def flip(key):
    st.session_state[key] = not st.session_state[key]


# state-dependent CSS (keeps widget values alive while panels are hidden)
dyn = f".st-key-charts_panel{{left:{300 if st.session_state.show_filters else 20}px;" \
      f"{'right:20px;' if st.session_state.show_charts else 'right:auto;'}}}"
if not st.session_state.show_filters:
    dyn += ".st-key-filters_panel{display:none !important;}"
if not st.session_state.show_charts:
    dyn += ".st-key-charts_row{display:none !important;}"
st.markdown(BASE_CSS + f"<style>{dyn}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        df = pd.read_parquet(PARQUET, columns=["grid_lat", "grid_lon", "year", "month", "harmonized_count"])
        df["year"] = df["year"].astype(int)
        df["harmonized_count"] = df["harmonized_count"].astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()


@st.cache_data
def parquet_bytes():
    with open(PARQUET, "rb") as f:
        return f.read()


hotspots = load_data()

# ---------------- header ----------------
st.markdown("""<div class="firms-header"><div>
<div class="logo-text">FIREWATCH</div><div class="logo-subtext">Satellite Fire Detection System</div>
</div></div>""", unsafe_allow_html=True)

st.button("☰", key="menu_btn", on_click=flip, args=("show_filters",), help="Show / hide filters")
st.download_button("Download", data=parquet_bytes(), file_name="harmonized_hotspots_canada_us.parquet",
                   mime="application/octet-stream", key="dl_btn", icon=":material/download:")


@st.dialog("Share FIREWATCH")
def share_dialog():
    st.write("Copy the link:")
    st.code(APP_URL, language=None)
    msg, u = quote("Explore wildfire activity across Canada and the US on FIREWATCH"), quote(APP_URL)
    st.markdown(
        f"[WhatsApp](https://wa.me/?text={msg}%20{u}) · [X](https://twitter.com/intent/tweet?text={msg}&url={u}) · "
        f"[LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url={u}) · [Email](mailto:?subject=FIREWATCH&body={msg}%20{u})")


@st.dialog("About FIREWATCH")
def about_dialog():
    st.write("FIREWATCH harmonizes MODIS and VIIRS satellite data to give a continuous, sensor-agnostic view "
             "of fire activity across Canada and the US from 2001 to 2025.")


if st.button("Share", key="share_btn", icon=":material/share:"):
    share_dialog()
if st.button("About", key="about_btn", icon=":material/info:"):
    about_dialog()

# ---------------- filters ----------------
CITIES = {"Toronto": (43.65, -79.38), "Vancouver": (49.28, -123.12), "Calgary": (51.05, -114.07),
          "Montreal": (45.50, -73.57), "New York": (40.71, -74.00), "Los Angeles": (34.05, -118.24),
          "Seattle": (47.60, -122.33), "Miami": (25.76, -80.19), "Chicago": (41.87, -87.62)}
lat_min, lat_max, lon_min, lon_max = 18.0, 84.0, -170.0, -50.0
region_name = "All Data"

with st.container(key="filters_panel"):
    selected_year = int(st.selectbox("Search Year", [str(y) for y in sorted(hotspots["year"].unique(), reverse=True)]))
    st.markdown("---")
    method = st.radio("Search Method", ["Country", "Nearest City", "Coordinates (Lat/Lon)", "Live Location"])

    if method == "Country":
        region_name = st.selectbox("Select Region", ["Canada", "United States"])
        lat_min, lat_max = (49.0, 84.0) if region_name == "Canada" else (18.0, 49.0)
    elif method == "Nearest City":
        region_name = st.selectbox("Select a Major City", list(CITIES))
        la, lo = CITIES[region_name]
        lat_min, lat_max, lon_min, lon_max = la - 2.5, la + 2.5, lo - 2.5, lo + 2.5
    elif method == "Coordinates (Lat/Lon)":
        lat_min = st.number_input("Min Latitude", value=18.0, step=1.0)
        lat_max = st.number_input("Max Latitude", value=84.0, step=1.0)
        lon_min = st.number_input("Min Longitude", value=-170.0, step=1.0)
        lon_max = st.number_input("Max Longitude", value=-50.0, step=1.0)
        region_name = "Custom Area"
    else:
        if st.button("Detect My Location"):
            lat_min, lat_max, lon_min, lon_max = 25.0, 60.0, -130.0, -60.0
            region_name = "Your Approximate Location"
        else:
            st.info("Click the button to center the map on your current region.")

region_df = hotspots[(hotspots["grid_lat"] >= lat_min) & (hotspots["grid_lat"] <= lat_max) &
                     (hotspots["grid_lon"] >= lon_min) & (hotspots["grid_lon"] <= lon_max)]

# ---------------- map (fixed, full canvas) ----------------
map_df = region_df[region_df["year"] == selected_year]
m = folium.Map(location=[(lat_min + lat_max) / 2, (lon_min + lon_max) / 2], zoom_start=3, min_zoom=3,
               tiles="Esri World Imagery", control_scale=True,
               min_lat=-85, max_lat=85, min_lon=-180, max_lon=180, max_bounds=True)
m.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])
if len(map_df):
    for r in map_df.sample(n=min(5000, len(map_df)), random_state=42).itertuples():
        folium.CircleMarker([r.grid_lat, r.grid_lon], radius=2.5, color="red", fill=True, fill_color="red",
                            fill_opacity=0.85,
                            tooltip=f"Lat: {r.grid_lat:.3f}<br>Lon: {r.grid_lon:.3f}<br>Year: {r.year}<br>Fires: {r.harmonized_count}").add_to(m)
st_folium(m, height=10, use_container_width=True, returned_objects=[])

# ---------------- glass chart panel (bottom) ----------------
GLASS = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=230,
             font=dict(family="Times New Roman", color="#1E3B2F", size=11))
CFG = {"displayModeBar": False}

monthly = region_df.groupby(["year", "month"])["harmonized_count"].sum().reset_index()
years = list(range(2001, 2026))
pivot = monthly.pivot(index="year", columns="month", values="harmonized_count").reindex(
    index=years, columns=range(1, 13)).fillna(0).astype(int)
totals = pivot.sum(axis=1)

fig_cal = go.Figure(go.Heatmap(
    z=pivot.values, x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    y=[str(y) for y in years], colorscale="YlOrRd", xgap=2, ygap=2, zmin=0,
    hovertemplate="Year: %{y}<br>Fires: %{z}<extra></extra>", colorbar=dict(thickness=8, len=0.9, tickformat=",d")))
yi = years.index(selected_year)
fig_cal.add_shape(type="rect", x0=-.5, x1=11.5, y0=yi - .5, y1=yi + .5, line=dict(color="#1E3B2F", width=3))
fig_cal.update_layout(**GLASS, margin=dict(l=40, r=5, t=5, b=25),
                      xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                      yaxis=dict(autorange="reversed", type="category", showgrid=False, tickfont=dict(size=8)))

fig_trend = go.Figure(go.Scatter(x=years, y=totals.values, mode="lines+markers", fill="tozeroy",
                                 fillcolor="rgba(30,59,47,.18)", line=dict(width=3, color="#1E3B2F"),
                                 marker=dict(size=5, color="#1E3B2F"),
                                 hovertemplate="Year: %{x}<br>Fires: %{y:,d}<extra></extra>"))
fig_trend.add_annotation(x=selected_year, y=int(totals[selected_year]), text="▼", showarrow=False,
                         font=dict(color="red", size=18), yshift=12)
fig_trend.update_layout(**GLASS, margin=dict(l=55, r=15, t=5, b=30), dragmode="pan",
                        xaxis=dict(title="Year", gridcolor="rgba(200,180,138,.6)", linecolor="#1E3B2F", showline=True),
                        yaxis=dict(title="Harmonized Count", gridcolor="rgba(200,180,138,.6)", linecolor="#1E3B2F",
                                   showline=True, tickformat=",d"))

with st.container(key="charts_panel"):
    st.button("▼ Hide charts" if st.session_state.show_charts else "▲ Show charts",
              key="charts_btn", on_click=flip, args=("show_charts",))
    with st.container(key="charts_row"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h5>Burning Calendar</h5>", unsafe_allow_html=True)
            st.plotly_chart(fig_cal, use_container_width=True, config=CFG)
        with c2:
            st.markdown("<h5>Analytics Graph</h5>", unsafe_allow_html=True)
            st.plotly_chart(fig_trend, use_container_width=True, config=CFG)
