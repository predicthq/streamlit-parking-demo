import streamlit as st
import pandas as pd
import pydeck as pdk

def show_map(lat, lon, radius_meters, events):
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
                'ScatterplotLayer',
                data=[{"coordinates": [lon, lat], "radius": radius_meters}],
                get_position="coordinates",
                # radius_units="meters",
                filled=True,
                # stroked=True,
                get_color='[24, 161, 99, 40]',
                get_radius="radius",
            ),
            pdk.Layer(
                "ColumnLayer",
                data=point_events_df,
                get_position=["lon", "lat"],
                auto_highlight=True,
                pickable=True,
                extruded=True,
                get_elevation="phq_attendance / 30",
                opacity=0.8,
                radius=10,
                stroked=False,
                filled=True,
                get_fill_color="fill_color",
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