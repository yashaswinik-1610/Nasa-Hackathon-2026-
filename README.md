# MV-Sat: Harmonized MODIS-VIIRS Satellite Fire Detection System


**Live Web Application:** https://nasa-hackathon-2026-mv-sat-jx7dmzc5v78pvxslqczmeq.streamlit.app/                                                                        
**Project Demonstration:** https://drive.google.com/drive/folders/17cLns69INU93bj6USnIXpaa126jpPuuM?usp=sharing


## Overview

Wildfire management requires a reliable, long-term view of fire history. However, comparing older satellite data (MODIS) with newer data (VIIRS) presents a major challenge. VIIRS has a higher spatial resolution (375m) and detects roughly 6x more fires than MODIS (1km). A naïve merge creates a fake spike in 2012 when VIIRS was launched.

**MV-Sat** solves this by harmonizing the datasets. We calculated the overlap ratio between the sensors (2012-2025) and applied a bias correction to the historical MODIS data. the result is a continuous, sensor-agnostic dataset from 2001 to 2025 for Canada and the United States. The web application then visualizes this data through an interactive, user-friendly dashboard designed for emergency managers and scientists.


## Key Features

- **Interactive Satellite Map:** Built with Folium and Esri World Imagery. Includes smooth zoom/pan, glassmorphism tooltips (Latitude/Longitude/Year/Fires) and a reset view button.
- **Burning Calendar:** A GitHub-contribution-style heatmap showing historical fire intensity. Designed with an accessible light-to-dark red color ramp.
- **Analytics & Anomalies:**
  - *Trend Graph:* Compares the selected year against the 25-year multi-year average (dotted line).
  - *Anomalies Graph:* Highlights exactly how much a specific year deviated from the historical baseline (red for above-average< blue for below-average).
- **Search & Filter:** Users can search by Country, Nearest Major City, or Custom Latitude/Longitude Coordinates.


## Methodology & Data Processing Pipeline

Our data pipeline is designed to ingest millions of raw satellite detections, filter out noise, and mathematically align the two different sensors into a single, consistent time series.

### 1. Data Ingestion & Pre-Processing
- **Chunking:** Because the raw FIRMS CSVs are massive (over 50,000 rows per file), they are read in chunks using `pandas` to prevent memory overflow.
- **Schema Standardization:** MODIS and VIIRS have different column names for the same physical measurements. The algorithm used to unify them:
  - `brightness` (MODIS) and `bright_ti4` (VIIRS) into a standard `brightness_k` column.
  - Dates are parsed using `pd.to_datetime()` with errors coerced to null.
 
### 2. Quality Screening & Filtering Algorithms
To ensure we are only looking at high-confidence fire events, we apply strict filtering logic:
- **Confidence Filtering:**
   - *MODIS:* The `confidence` column is a numeric percentage (0-100). We drop all rows with a confidence score of `<80`.
   - *VIIRS:* The `confidence` column is next (`l`, `n`, `h`). We map these to integers (0, 1, 2) and keep only `nominal` (1) and `high` (2) confidence detections.
- **Type Filtering:** For VIIRS data, we filter for `type == 0` to ensure we are only looking at vegetation fires (excluding volcanic activity or gas flares).
- **Spatial Bounding Box Filtering:** Detections outside of North America (Latitude 18° to 84°N, Longitude 50° to 170°W) are removed to focus the study on Canada and the US.

### 3. Spatial Gridding Algorithm (1km Resolution)
To compare the two sensors, the data must be mapped to a common spatial grid.
- **Algorithm:** We round the raw floating-point coordinates to the nearest `0.01` degree (approximately 1.1km at the equator).
- **Implementation:**
     ```python
  grid_iy = np.round(latitude / 0.01).astype("int32")
  grid_ix = np.round(longitude / 0.01).astype("int32")
  grid_id = grid_iy.astype(str) + "_" + grid_ix.astype(str)

 ### 4. Harmonization Algorithm (Overlap-Based Bias Correction)
 To remove the sensor bias, we use the years where both satellites were active (2012-2025) to learn the statistical relationship between them.
- **Step A (Overlap):** Group the 2012-2025 data by `grid_id` and `month`, counting the total MODIS detections and total VIIRS detections.
- **Step B (Ratio Calculation):** Calculate `ratio = VIIRS_count / MODIS_count`.
- **Step C (Noise Reduction):** Filter out grid cells where `MODIS_count < 2` to prevent division-by-zero errors and statistical noise. Clip extreme outliers between `0.5` and `50.9`.
- **Step D (median):** Calculate the global median ratio. **Result: 6.00** (Meaning VIIRS detects 6 times as many fires as MODIS in the same cell/month).
- **Step E (Correction):** For the pre-2012 era, multiply the raw MODIS counts by the learned local ratio (or the global median of 6.00 if local data is missing).
- **Step F (Concatenation):** Combine the corrected pre-2012 data with the post-2012 VIIRS data to create a seamless 25-year time series.


## Third-Party Libraries & Tools Used

The application is built entirely in Python and utilizes the following open-source libraries:
- [Streamlit](https://streamlit.io/): The core framework for building the interactive web application.
- [Pandas](https://pandas.pydata.org/): Data manipulation, filtering, and aggregation.
- [PyArrow](https://arrow.apache.org/): Efficient reading of the compressed Parquet dataset.
- [Plotly](https://plotly.com/python/): Interactive graphs, including the heatmap calendar and anomaly bar charts.
- [Folium](https://python-visualization.github.io/folium/): Generating the interactive satellite map.
- [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium): Integrating the Folium map into Streamlit.
- [NumPy](https://numpy.org/): Mathematical operations during data preprocessing.


## Data Source

The raw data was sourced from NASA FIRMS [Fire Information for Resource Management System](https://firms.modaps.eosdis.nasa.gov/download/). Specifically, the data was downloaded for Canada and US. The dataset includes:
- MODIS (2001-2025)
- VIIRS S-NPP (2012-2025)
- VIIRS NOAA-20 (2018-2025)


## How To Run Locally 

1. Clone this repository.
2. Install the required dependencies:
```
pip intall -r requirements.txt
```
3. Run the Streamlit app:
```
streamlit run app.py
```


## Future Scope

- **Global Scaling:** While this proof-of-concept focuses on Canada and the US, the Dockerized pipeline can be immediately scaled to process global FIRMS data.
- **Real-Time Integration:** The architecture is designed to ingest near-real-time FIRMS data (last 24 hours). Emergency managers could compare a fire happening today against the 25-year historical baseline for the exact location.
- **Fire Progess Timeline (Dynamic Tracking):** Currently, MV-Sat visualizes historical fire data aggregated by month and year. A future iteration will integrate near-real-time (NRT) FIRMS data to provide a dynamic, day-by-day timeline of active fires. Users will be able to track exactly when a specific fire event started, how it spread over time, and compare its current growth trajectory against historical baseline fires for that region.
- **Predictive Modeling:** The harmonized dataset provides a clean foundation for training machine learning models to predict fire severity based on historical anomalies and weather patterns.


## AI Tools Disclosure

In the spirit of transparency and modern development practices, we utilized AI Large Language Models ([Gemini](https://gemini.google.com/), [Claude](https://claude.ai/), [Grok](https://grok.com/) as coding assistances. Their role was strictly limited to :
- Debugging memory and deployment issues during the transition from local to cloud environments.
- Assisting with the advances CSS/HTML injection to achieve the glassmorphism UI.
- Drafting documentation.

All data processing logic, the spatial gridding algorithm, the harmonization methodology and the scientific validation of the results were designed and implemented by the team. 


## Team

- Yashaswini K
- Jose Miguel Jaramillo Betancur
