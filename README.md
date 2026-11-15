# MV-Sat: Harmonized MODIS-VIIRS Satellite Fire Detection System


**Live Web Application:** https://nasa-hackathon-2026-mv-sat-jx7dmzc5v78pvxslqczmeq.streamlit.app/


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



