import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

def show_map(lat, lon, events):
    # df = pd.DataFrame(
    #     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    #     columns=['lat', 'lon'])

    # TODO - convert events to a dataframe
    # when displaying layer, filter for just point types and then on polygon layer filter just for polygons...
    COLOR_RANGE = [
        [246, 213, 141],
        [246, 198, 132],
        [246, 184, 124],
        [246, 169, 115],
        [245, 155, 107],
        [245, 140, 98],
        [245, 126, 90],
        [245, 111, 81],
        [245, 96, 72],
        [245, 82, 64],
        [244, 67, 55],
        [244, 53, 47],
        [244, 38, 38],
    ]

    BREAKS = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000]

    def color_scale(val):
        for i, b in enumerate(BREAKS):
            if val < b:
                return COLOR_RANGE[i]
        return COLOR_RANGE[i]
    
    point_results = []

    for event in events["results"]:
        row = {
            "id": event["id"],
            "title": event["title"],
            "phq_attendance": event["phq_attendance"] if event["phq_attendance"] else "0",
            "phq_attendance_formatted": "{:,}".format(event["phq_attendance"]) if event["phq_attendance"] else "0",
            "category": event["category"],
            "lat": event["geo"]["geometry"]["coordinates"][1],
            "lon": event["geo"]["geometry"]["coordinates"][0],
            "fill_color": color_scale(event["phq_attendance"] if event["phq_attendance"] else 0),
        } if event["geo"]["geometry"]["type"] == "Point" else None

        if row:
            point_results.append(row)

    point_events_df = pd.DataFrame(point_results)

    # TODO - non-point events


    # geojson_features = []

    # for event in events["results"]:
    #     geojson_features.append({
    #         "type": "Feature",
    #         # "geometry": {
    #         #     "type": event["geo"]["geometry"]["type"],
    #         #     "coordinates": [event["geo"]["geometry"]["coordinates"][1], event["geo"]["geometry"]["coordinates"][0]],
    #         # },
    #         "geometry": event["geo"]["geometry"],
    #         "properties": {
    #             "id": event["id"],
    #             "title": event["title"],
    #             "phq_attendance": event["phq_attendance"],
    #         }
    #     })

    # feature_collection = {
    #     "type": "FeatureCollection",
    #     "features": geojson_features,
    # }

    # st.write(geojson_features)

    # st.write(lat, lon)

    

    # st.dataframe(point_events_df)
    
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        tooltip={
            "html": """
                <p><b>{title}</b></p>
                Predicted Attendance: {phq_attendance_formatted}<br />
                Category: {category}
            """,
        },
        initial_view_state=pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=14,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "ColumnLayer",
                data=point_events_df,
                get_position=["lon", "lat"],
                # get_position="geometry.coordinates",
                # line_width_min_pixels=1,
                auto_highlight=True,
                # # elevation_scale=50,
                pickable=True,
                # elevation_range=[0, 500],
                extruded=True,
                get_elevation="phq_attendance / 30",
                # # coverage=1,
                opacity=0.8,
                radius=10,
                stroked=False,
                filled=True,
                # point_type="circle",
                # # extruded=True,
                # wireframe=True,
                # get_elevation="properties.valuePerSqm / 20",
                # get_fill_color="[phq_attendance / 20, 130, 121, 255]",
                get_fill_color="fill_color",
                # get_line_color=[255, 255, 255],
            ),
            # pdk.Layer(
            #     'GeoJsonLayer',
            #     data=geojson_features,
            #     # get_position=["lon", "lat"],
            #     auto_highlight=True,
            #     pickable=True,
            #     get_fill_color='[200, 30, 0, 160]',
            #     get_radius=1,
            #     opacity=0.8,
            #     # extruded=True,
            #     # get_elevation="properties.phq_attendance / 200",
            # ),
        ],
    ))

    # st.map(df)