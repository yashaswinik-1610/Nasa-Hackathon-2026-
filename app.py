import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Harmonized Fire Calendar", layout="wide")

@st.cache_data
def load_data():
    parquet_file = "harmonized_hotspots_canada_us.parquet"
  
    file_id = "1L23_KvxHTAc_noGlp3z2j4ZVK-n7pmf_"

    if not os.path.exists(parquet_file):
       
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        with st.spinner("Downloading large dataset from Google Drive... Please wait."):
            response = requests.get(url, headers=headers)
            response.raise_for_status() 
           
            
            if b'<!DOCTYPE html>' in response.content[:100]:
                st.warning("Google Drive returned a confirmation page. Trying to extract the direct link...")
                
                import re
                match = re.search(r'href="(/uc\?export=download[^"]+)"', response.text)
                if match:
                    direct_link = "https://drive.google.com" + match.group(1).replace("&amp;", "&")
                    response = requests.get(direct_link, headers=headers)
                    response.raise_for_status()
                else:
                    st.error("Could not find the direct download link on the Google Drive confirmation page. Please try 'Solution 1' or an alternative hosting method.")
                    st.stop()

            
            with open(parquet_file, "wb") as f:
                f.write(response.content)
    
    hotspots = pd.read_parquet(parquet_file)
    monthly = pd.read_csv("processed_data/harmonized_monthly_summary.csv")
    return hotspots, monthly

try:
    hotspots, monthly = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()
