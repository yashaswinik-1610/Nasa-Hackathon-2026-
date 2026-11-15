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

