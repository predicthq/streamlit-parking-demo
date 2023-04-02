import streamlit as st
import datetime
import requests
import pandas as pd
from utils.pages import set_page_config
from utils.sidebar import show_sidebar_options, show_map_sidebar_code_examples
from utils.metrics import show_metrics
from utils.predicthq import (
    get_api_key,
    fetch_events,
    ATTENDED_CATEGORIES,
    NON_ATTENDED_CATEGORIES,
    UNSCHEDULED_CATEGORIES,
)
from utils.map import show_map


def main():
    set_page_config("Map")
    show_sidebar_options()

    if get_api_key() is not None:
        map()
    else:
        st.warning("Please set a PredictHQ API Token.", icon="⚠️")


def map():
    location = st.session_state.location if "location" in st.session_state else None
    daterange = st.session_state.daterange if "daterange" in st.session_state else None
    suggested_radius = (
        st.session_state.suggested_radius
        if "suggested_radius" in st.session_state
        else None
    )
    radius = st.session_state.radius if "radius" in st.session_state else None

    if (
        location is None
        or daterange is None
        or suggested_radius is None
        or radius is None
    ):
        return

    st.header(location["name"])

    # Display metrics
    show_metrics()

    # Pull out date range to make them easier to work with
    date_from = daterange["date_from"]
    date_to = daterange["date_to"]

    # Allow selecting categories
    categories = ATTENDED_CATEGORIES + NON_ATTENDED_CATEGORIES + UNSCHEDULED_CATEGORIES
    default_categories = ATTENDED_CATEGORIES
    selected_categories = st.sidebar.multiselect(
        "Event categories",
        options=categories,
        default=default_categories,
        help="[Event Categories Docs](https://docs.predicthq.com/resources/events)",
    )

    # We have a bunch of code examples in the docs/code_examples folder
    show_map_sidebar_code_examples()

    # Fetch events
    events = fetch_events(
        location["lat"],
        location["lon"],
        radius,
        date_from=date_from,
        date_to=date_to,
        categories=selected_categories,
    )

    # Show map and convert radius miles to meters (the map only supports meters)
    show_map(
        lat=location["lat"],
        lon=location["lon"],
        radius_meters=radius * 1609,
        events=events,
    )

    show_events_list(events, f'events-{location["id"]}-{date_from}-to-{date_to}')


def show_events_list(events, filename="events"):
    results = []

    for event in events["results"]:
        venue = next(
            filter(lambda entity: entity["type"] == "venue", event["entities"]), None
        )

        row = {
            "id": event["id"],
            "title": event["title"],
            "phq_attendance": event["phq_attendance"] if event["phq_attendance"] else 0,
            "category": event["category"],
            "start_date": event["start"],  # TODO convert from UTC to local
            "end_date": event["end"],
            "predicted_end_date": event["predicted_end"],
            "venue_name": venue["name"] if venue else "",
            "venue_address": venue["formatted_address"] if venue else "",
            "placekey": event["geo"]["placekey"]
            if "geo" in event and "placekey" in event["geo"]
            else "",
        }

        results.append(row)

    events_df = pd.DataFrame(results)
    st.dataframe(events_df)

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    csv = convert_df(events_df)

    st.download_button(
        label="✅ Download events as CSV",
        data=csv,
        file_name=f"{filename}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
