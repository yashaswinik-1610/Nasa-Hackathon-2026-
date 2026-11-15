from urllib.parse import quote

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
import streamlit.components.v1 as components

APP_URL = "https://your-app-name.streamlit.app"   # <<< your deployed link (used by Share)
PARQUET = "Processed Data/harmonized_hotspots_canada_us.parquet"
RAW_URL = "https://github.com/yashaswinik-1610/Nasa-Hackathon-2026-/raw/main/Processed%20Data/harmonized_hotspots_canada_us.parquet"
FONT = "'Google Sans Flex','Google Sans','Product Sans',Arial,sans-serif"

st.set_page_config(page_title="FIREWATCH", layout="wide", initial_sidebar_state="collapsed")

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@400;600;700&display=swap');
:root {--c0:#000000; --c1:#830000; --c2:#BC0202; --c3:#FF0000;}
html, body, [class*="css"], .stApp p, .stApp label, .stApp h5, .stApp button p, .stApp a p, .stApp span[data-baseweb] {
  font-family:'Google Sans Flex','Google Sans','Product Sans',Arial,sans-serif !important;}
.stApp {background:var(--c0) !important; color:#fff !important;}
.stApp, [data-testid="stAppViewContainer"], section.main {overflow:hidden !important;}
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"], [data-testid="stElementToolbar"], #MainMenu, footer {display:none !important;}
.block-container {padding:0 !important; max-width:100% !important;}
p, label, h5 {color:#fff !important;}

.firms-header {position:fixed; top:0; left:0; width:100%; height:85px; background:var(--c1); display:flex; align-items:center;
  padding:0 25px 0 80px; box-shadow:0 2px 10px rgba(0,0,0,.6); z-index:999999;}
.logo-text {font-size:28px; font-weight:700; letter-spacing:1px; color:#fff; line-height:1;}
.logo-subtext {font-size:14px; margin-top:2px; color:#fff; opacity:.9;}

.st-key-menu_btn, .st-key-dl_btn, .st-key-share_btn, .st-key-about_btn {position:fixed; top:20px; z-index:1000001;}
.st-key-menu_btn {left:18px;} .st-key-about_btn {right:25px;} .st-key-share_btn {right:150px;} .st-key-dl_btn {right:265px;}
.st-key-menu_btn button, .st-key-share_btn button, .st-key-about_btn button, .st-key-dl_btn a {
  background:transparent !important; border:0 !important; box-shadow:none !important; color:#fff !important;}
.st-key-menu_btn button:hover, .st-key-share_btn button:hover, .st-key-about_btn button:hover, .st-key-dl_btn a:hover {background:var(--c2) !important;}
.st-key-menu_btn button p {font:700 32px Arial !important; line-height:1;}
.st-key-share_btn button p, .st-key-about_btn button p, .st-key-dl_btn a p {font-size:17px !important; font-weight:600 !important;}

/* map = fixed full window below header */
.st-key-map_box iframe {position:fixed !important; top:85px; left:0; width:100vw !important; height:calc(100vh - 85px) !important; z-index:1; border:0;}

.st-key-filters_panel {position:fixed; top:100px; left:14px; width:270px; max-height:calc(100vh - 130px); overflow-y:auto; z-index:1000;
  background:var(--c0); border:1px solid var(--c2); border-radius:15px; padding:14px; box-shadow:0 4px 16px rgba(0,0,0,.7);}
.st-key-filters_panel label p {font-size:1.05rem !important; font-weight:700 !important;}
.st-key-filters_panel [data-baseweb="select"] > div, .st-key-filters_panel input {background:#1a0000 !important; color:#fff !important;}

/* chart switcher: ONLY these two buttons are glass */
.st-key-chart_pick {position:fixed; bottom:18px; left:50%; transform:translateX(-50%); width:440px; z-index:1002; padding:6px 8px;
  background:rgba(0,0,0,.45); backdrop-filter:blur(14px) saturate(150%); -webkit-backdrop-filter:blur(14px) saturate(150%);
  border:1px solid rgba(255,0,0,.5); border-radius:999px; box-shadow:0 8px 32px rgba(0,0,0,.6);}
.st-key-chart_pick button {background:transparent !important; border:0 !important; border-radius:999px !important; padding:6px 10px !important;}
.st-key-chart_pick button:hover {background:rgba(188,2,2,.4) !important;}
.st-key-chart_pick button p {font-size:1.05rem !important; font-weight:700 !important; color:#fff !important;}
/* chart view: solid panel that opens above the switcher */
.st-key-charts_panel {position:fixed; bottom:78px; z-index:1001; padding:10px 14px; background:#0b0000;
  border:1px solid var(--c2); border-radius:14px; box-shadow:0 8px 32px rgba(0,0,0,.7);}
.hdl {position:fixed; top:20px; right:265px; z-index:1000001; color:#fff !important; font-size:17px; font-weight:600;
  padding:8px 12px; border-radius:6px; text-decoration:none !important;}
.hdl:hover {background:var(--c2);}
</style>
"""

for k in ("show_filters", "show_charts"):
    st.session_state.setdefault(k, True)


def flip(k):
    st.session_state[k] = not st.session_state[k]


_left = 300 if st.session_state.show_filters else 20
dyn = f".st-key-charts_panel{{left:{_left}px;width:calc(100vw - {_left + 20}px);}}"
if not st.session_state.show_filters:
    dyn += ".st-key-filters_panel{display:none !important;}"
st.markdown(BASE_CSS + f"<style>{dyn}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_parquet(PARQUET, columns=["grid_lat", "grid_lon", "year", "month", "harmonized_count"])
    df["year"] = df["year"].astype("int16")
    df["harmonized_count"] = df["harmonized_count"].astype("int32")
    return df


hotspots = load_data()


@st.cache_data(show_spinner=False)
def chart_data(b):
    d = hotspots[(hotspots.grid_lat >= b[0]) & (hotspots.grid_lat <= b[1]) & (hotspots.grid_lon >= b[2]) & (hotspots.grid_lon <= b[3])]
    pv = d.groupby(["year", "month"])["harmonized_count"].sum().unstack(fill_value=0)
    return pv.reindex(index=range(2001, 2026), columns=range(1, 13), fill_value=0)


@st.cache_data(show_spinner=False, max_entries=24)
def map_html(year, b):
    d = hotspots[(hotspots.year == year) & (hotspots.grid_lat >= b[0]) & (hotspots.grid_lat <= b[1]) &
                 (hotspots.grid_lon >= b[2]) & (hotspots.grid_lon <= b[3])]
    m = folium.Map(location=[(b[0] + b[1]) / 2, (b[2] + b[3]) / 2], zoom_start=3, min_zoom=3, tiles="Esri World Imagery",
                   prefer_canvas=True, min_lat=-85, max_lat=85, min_lon=-180, max_lon=180, max_bounds=True)
    m.fit_bounds([[b[0], b[2]], [b[1], b[3]]])
    if len(d):
        for r in d.sample(n=min(3000, len(d)), random_state=42).itertuples():
            folium.CircleMarker([r.grid_lat, r.grid_lon], radius=2.5, color="#FF0000", fill=True, fill_color="#FF0000",
                                fill_opacity=0.85, weight=1,
                                tooltip=f"Lat: {r.grid_lat:.3f}<br>Lon: {r.grid_lon:.3f}<br>Year: {r.year}<br>Fires: {r.harmonized_count}").add_to(m)
    m.get_root().header.add_child(folium.Element(
        "<style>html,body{height:100%;margin:0}.leaflet-top.leaflet-left{top:auto;bottom:90px;left:auto;right:10px}</style>"))
    return m.get_root().render()


# ---------------- header ----------------
st.markdown('<div class="firms-header"><div><div class="logo-text">FIREWATCH</div>'
            '<div class="logo-subtext">Satellite Fire Detection System</div></div>'
            f'<a class="hdl" href="{RAW_URL}" target="_blank">&#11015; Download</a></div>', unsafe_allow_html=True)
st.button("☰", key="menu_btn", on_click=flip, args=("show_filters",), help="Show / hide filters")


@st.dialog("Share FIREWATCH")
def share_dialog():
    st.write("Copy the link:")
    st.code(APP_URL, language=None)
    msg, u = quote("Explore wildfire activity across Canada and the US on FIREWATCH"), quote(APP_URL)
    st.markdown(f"[WhatsApp](https://wa.me/?text={msg}%20{u}) · [X](https://twitter.com/intent/tweet?text={msg}&url={u}) · "
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
CITIES = {"Toronto": (43.65, -79.38), "Vancouver": (49.28, -123.12), "Calgary": (51.05, -114.07), "Montreal": (45.50, -73.57),
          "New York": (40.71, -74.00), "Los Angeles": (34.05, -118.24), "Seattle": (47.60, -122.33),
          "Miami": (25.76, -80.19), "Chicago": (41.87, -87.62)}
lat_min, lat_max, lon_min, lon_max = 18.0, 84.0, -170.0, -50.0

with st.container(key="filters_panel"):
    year = int(st.selectbox("Search Year", [str(y) for y in range(2025, 2000, -1)]))
    method = st.radio("Search Method", ["Country", "Nearest City", "Coordinates (Lat/Lon)", "Live Location"])
    if method == "Country":
        c = st.selectbox("Select Region", ["Canada", "United States"])
        lat_min, lat_max = (49.0, 84.0) if c == "Canada" else (18.0, 49.0)
    elif method == "Nearest City":
        la, lo = CITIES[st.selectbox("Select a Major City", list(CITIES))]
        lat_min, lat_max, lon_min, lon_max = la - 2.5, la + 2.5, lo - 2.5, lo + 2.5
    elif method == "Coordinates (Lat/Lon)":
        lat_min = st.number_input("Min Latitude", value=18.0, step=1.0)
        lat_max = st.number_input("Max Latitude", value=84.0, step=1.0)
        lon_min = st.number_input("Min Longitude", value=-170.0, step=1.0)
        lon_max = st.number_input("Max Longitude", value=-50.0, step=1.0)
    elif st.button("Detect My Location"):
        lat_min, lat_max, lon_min, lon_max = 25.0, 60.0, -130.0, -60.0
    else:
        st.info("Click the button to center the map on your current region.")

bounds = (float(lat_min), float(lat_max), float(lon_min), float(lon_max))

# ---------------- map ----------------
with st.container(key="map_box"):
    components.html(map_html(year, bounds), height=700)

# ---------------- glass chart panel (tabs: pick one) ----------------
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=240,
              font=dict(family="Google Sans Flex, Arial, sans-serif", color="#fff", size=11))


@st.fragment
def chart_panel(pv, yr):
    def toggle(name):
        st.session_state.open_chart = None if st.session_state.get("open_chart") == name else name

    with st.container(key="chart_pick"):
        a, b = st.columns(2)
        a.button("Burning Calendar", key="pill_cal", on_click=toggle, args=("cal",), use_container_width=True)
        b.button("Analytics Graph", key="pill_trend", on_click=toggle, args=("trend",), use_container_width=True)
    cur = st.session_state.get("open_chart")
    if not cur:
        return
    st.markdown(f"<style>.st-key-pill_{cur} button{{background:#BC0202 !important;}}</style>", unsafe_allow_html=True)
    years = list(pv.index)
    with st.container(key="charts_panel"):
        if cur == "cal":
            fig = go.Figure(go.Heatmap(z=pv.values, x=MONTHS, y=[str(y) for y in years], xgap=2, ygap=2, zmin=0,
                                       colorscale=[[0, "#000000"], [.35, "#830000"], [.7, "#BC0202"], [1, "#FF0000"]],
                                       hovertemplate="Year: %{y}<br>Fires: %{z}<extra></extra>",
                                       colorbar=dict(thickness=8, len=.9, tickformat=",d")))
            i = years.index(yr)
            fig.add_shape(type="rect", x0=-.5, x1=11.5, y0=i - .5, y1=i + .5, line=dict(color="#fff", width=2))
            fig.update_layout(**LAYOUT, margin=dict(l=40, r=5, t=5, b=25),
                              xaxis=dict(showgrid=False), yaxis=dict(autorange="reversed", type="category", showgrid=False, tickfont=dict(size=8)))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            tot = pv.sum(axis=1)
            fig = go.Figure(go.Scatter(x=years, y=tot.values, mode="lines+markers", fill="tozeroy", fillcolor="rgba(255,0,0,.18)",
                                       line=dict(width=3, color="#FF0000"), marker=dict(size=5, color="#FF0000"),
                                       hovertemplate="Year: %{x}<br>Fires: %{y:,d}<extra></extra>"))
            fig.add_annotation(x=yr, y=int(tot[yr]), text="▼", showarrow=False, font=dict(color="#fff", size=18), yshift=12)
            grid = "rgba(255,255,255,.15)"
            fig.update_layout(**LAYOUT, margin=dict(l=60, r=15, t=5, b=35), dragmode="pan",
                              xaxis=dict(title="Year", gridcolor=grid), yaxis=dict(title="Harmonized Count", gridcolor=grid, tickformat=",d"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


chart_panel(chart_data(bounds), year)
