import streamlit as st
import datetime
from utils.predicthq import get_api_key, get_predicthq_client
from utils.code_examples import get_code_example


def show_sidebar_options():
    # TODO - get list of actual parking buildings across the globe
    locations = [
        {
            "id": "san-francisco",
            "name": "San Francisco, USA",
            "lat": 37.78690,
            "lon": -122.40152,
        },
        {"id": "new-york", "name": "New York, USA", "lat": 40.71, "lon": -74.01},
        {"id": "los-angeles", "name": "Los Angeles, USA", "lat": 34.05, "lon": -118.24},
        {"id": "london", "name": "London, UK", "lat": 51.50088, "lon": -0.14098},
        {"id": "paris", "name": "Paris, FR", "lat": 48.86487, "lon": 2.35002},
        {"id": "berlin", "name": "Berlin, DE", "lat": 52.50542, "lon": 13.33851},
    ]

    index = (
        locations.index(st.session_state.location)
        if "location" in st.session_state
        else 0
    )
    location = st.sidebar.selectbox(
        "Parking Building",
        locations,
        index=index,
        format_func=lambda x: x["name"],
        help="Select the parking building location.",
        disabled=get_api_key() is None,
        key="location",
    )

    # Prepare the date range (today + 30d as the default)
    today = datetime.date.today()
    date_options = [
        {
            "name": "Next 7 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=7),
        },
        {
            "name": "Next 30 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=30),
        },
        {
            "name": "Next 90 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=90),
        },
    ]

    index = (
        date_options.index(st.session_state.daterange)
        if "daterange" in st.session_state
        else 0
    )
    st.sidebar.selectbox(
        "Date Range",
        date_options,
        index=index,
        format_func=lambda x: x["name"],
        help="Select the date range for fetching event data.",
        disabled=get_api_key() is None,
        key="daterange",
    )

    st.session_state.suggested_radius = fetch_suggested_radius(
        location["lat"], location["lon"]
    )

    # Allow changing the radius if needed (default to suggested radius)
    # The Suggested Radius API is used to determine the best radius to use for the given location and industry
    st.sidebar.slider(
        "Suggested Radius around parking building (mi)",
        0.0,
        10.0,
        st.session_state.suggested_radius.get("radius", 2.0),
        0.1,
        help="[Suggested Radius Docs](https://docs.predicthq.com/resources/suggested-radius)",
        key="radius",
    )


@st.cache_data
def fetch_suggested_radius(lat, lon, radius_unit="mi", industry="parking"):
    phq = get_predicthq_client()
    suggested_radius = phq.radius.search(
        location__origin=f"{lat},{lon}", radius_unit=radius_unit, industry=industry
    )

    return suggested_radius.to_dict()


def show_map_sidebar_code_examples():
    st.sidebar.markdown("## Code examples")

    # The code examples are saved as markdown files in docs/code_examples
    examples = [
        {"name": "Suggested Radius API", "filename": "suggested_radius_api"},
        {
            "name": "Features API (Predicted Attendance aggregation)",
            "filename": "features_api",
        },
        {"name": "Count of Events", "filename": "count_api"},
        {"name": "Demand Surge API", "filename": "demand_surge_api"},
        {"name": "Search Events", "filename": "events_api"},
        {"name": "Python SDK for PredictHQ APIs", "filename": "python_sdk"},
    ]

    for example in examples:
        with st.sidebar.expander(example["name"]):
            st.markdown(get_code_example(example["filename"]))

    st.sidebar.caption(
        "Get the code for this app at [GitHub](https://github.com/predicthq/streamlit-parking-demo)"
    )
