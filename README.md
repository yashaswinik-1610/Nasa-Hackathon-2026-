# MV-Sat: Harmonized MODIS-VIIRS Satellite Fire Detection System


**Live Web Application:** https://nasa-hackathon-2026-mv-sat-jx7dmzc5v78pvxslqczmeq.streamlit.app/


# Overview

Wildfire management requires a reliable, long-term view of fire history. However, comparing older satellite data (MODIS) with newer data (VIIRS) presents a major challenge. VIIRS has a higher spatial resolution (375m) and detects roughly 6x more fires than MODDIS (1km). A naïve merge creates a fake spike in 2012 when VIIRS was launched.

**MV-Sat** solves this by harmonizing the datasets. We calculated the overlap ratio between the sensors (2012-2025) and applied a bias correction to the historical MODIS data. The result is a continuous, sensor-agnostic dataset from 2001 to 2025 for Canada and the United States. The web application then visualizes this data through an interactive, user-friendly dashboard designed for emergency managers and scientists.


## Key Features

- **Interactive Satellite Map:** Built with Folium and Esri World Imagery. Includes smooth zoom/pan, glassmorphism tooltips (Latitude/Longitude/Year/Fires), and a reset view button.
- **Burning Calendar:** A GitHub-contribution-style heatmap showing historical fire intensity. Designed with an accessible light-to-dark red color ramp.
- **Analytics & Anomalies:**
   - *Trend Graph:* Compares the selected year against the 25-year multi-year average (dotted line).
   - *Anomalies Graph:* Highlights exactly how much a specific year deviated from the historical                             base-line (red for above-average, blue for below-average).
- **Filtered CSV Export:** Users can download the exact hotspot data for their currently selected region and year.
- **Search & Filter:** Users can search by country, Nearest Major City, or Custom Latitude/Longitude coordinates.


## Methodology: Overlap-Based Bias Correction

1. **Gridding:** Both MODIS-VIIRS hotspots were mapped to a common ~1km grid cell (0.01° resolution).
2. **Overlap Calculation:** During the 2012-2025 overlap period, we calculated the median ratio of VIIRS detections to MODIS detections per grid cell and month.
3. **Correction:** The median ratio was found to be 6.00. We applied this ratio to pre-2012 MODIS counts to estimate what VIIRS would have detected.
4. **Quality Filtering:** MODIS detections were filtered to >= 80% confidence; VIIRS was filtered to nominal and high confidence.


## Third-Part Libraries & Tools Used

The application is built in Python and utilizes the following open-source libraries:
- **

