# ----- MAP (stretched / wide) -----
with col_map:
    st.markdown("<h3 style='text-align:center; margin-bottom:4px;'>Map</h3>", unsafe_allow_html=True)
    map_data = region_df[region_df["year"] == selected_year]

    if len(map_data) > 0:
        # Sample for performance
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
        
        # Fixed layout – use "map" instead of "mapbox"
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="#F5F0E6",
            map=dict(                   # ← changed from mapbox to map
                center=dict(lat=48, lon=-100)
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning(f"No data available for {country} in {selected_year}.")
