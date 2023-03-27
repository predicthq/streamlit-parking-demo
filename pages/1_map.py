import streamlit as st
import time
import pandas as pd
from utils.pages import set_page_config
from utils.sidebar import show_sidebar_options
from utils.predicthq import get_api_key, get_predicthq_client
from utils.data import flatten_dict
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

    if location is None or daterange is None:
        return
    
    st.header(location["name"])
    st.caption(f"{location['lat']}, {location['lon']}")
    
    suggested_radius = fetch_suggested_radius(location["lat"], location["lon"])

    with st.container():
        # Allow changing the radius if needed (default to suggested radius)
        radius = st.slider("Radius around parking building in miles", 0.0, 10.0, suggested_radius.get("radius", 2.0), 0.1, help="Events will be fetched within this radius around the parking building.")

    with st.container():
        # Allow selecting categories
        attended_categories = [
            "community",
            "concerts",
            "conferences",
            "expos",
            "festivals",
            "performing-arts",
            "sports",
        ]
        non_attended_categories = [
            "academic",
            "daylight-savings",
            "observances",
            "politics",
            "public-holidays",
            "school-holidays",
        ]
        unscheduled_categories = [
            "airport-delays",
            "disasters",
            "health-warnings",
            "severe-weather",
            "terror",
        ]
        categories = attended_categories + non_attended_categories + unscheduled_categories
        default_categories = attended_categories

        selected_categories = st.multiselect("Event categories", options=categories, default=default_categories, help="[Event Categories Docs](https://docs.predicthq.com/resources/events)")

    if len(daterange) == 2:
        # Work out previous date range for comparisons
        previous_date_from = daterange[0] - (daterange[1] - daterange[0])
        previous_date_to = daterange[0]

        # Fetch event counts/stats
        counts = fetch_event_counts(location["lat"], location["lon"], radius, date_from=daterange[0], date_to=daterange[1])
        attended_events_sum = calc_sum_of_event_counts(counts, attended_categories)
        non_attended_events_sum = calc_sum_of_event_counts(counts, non_attended_categories)

        # Fetch event counts/stats for previous period
        previous_counts = fetch_event_counts(location["lat"], location["lon"], radius, date_from=previous_date_from, date_to=previous_date_to)
        previous_attended_events_sum = calc_sum_of_event_counts(previous_counts, attended_categories)
        previous_non_attended_events_sum = calc_sum_of_event_counts(previous_counts, non_attended_categories)
        
        # Fetch sum of Predicted Attendance
        features = [
            # "phq_attendance_academic_graduation",
            # "phq_attendance_academic_social",
            "phq_attendance_community",
            "phq_attendance_concerts",
            "phq_attendance_conferences",
            "phq_attendance_expos",
            "phq_attendance_festivals",
            "phq_attendance_performing_arts",
            "phq_attendance_sports",
            # "phq_attendance_school_holidays",
        ]
        phq_attendance_features = fetch_features(location["lat"], location["lon"], radius, date_from=daterange[0], date_to=daterange[1], features=features)
        phq_attendance_sum = calc_sum_of_features(phq_attendance_features, features)

        # Fetch previous predicted attendance
        previous_phq_attendance_features = fetch_features(location["lat"], location["lon"], radius, date_from=previous_date_from, date_to=previous_date_to, features=features)
        previous_phq_attendance_sum = calc_sum_of_features(previous_phq_attendance_features, features)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="Suggested Radius", value=f"{suggested_radius['radius']}{suggested_radius['radius_unit']}", help="[Suggested Radius Docs](https://docs.predicthq.com/resources/suggested-radius)")

        with col2:
            delta_pct = (phq_attendance_sum - previous_phq_attendance_sum) / previous_phq_attendance_sum * 100
            st.metric(label="Predicted Attendance", value=f"{phq_attendance_sum:,.0f}", delta=f"{delta_pct:,.0f}%", help=f"The predicted number of people attending events in the selected date range. Previous period: {previous_phq_attendance_sum:,.0f}.")

        with col3:
            delta_pct = (attended_events_sum - previous_attended_events_sum) / previous_attended_events_sum * 100
            st.metric(label="Attended Events", value=attended_events_sum, delta=f"{delta_pct:,.0f}%", help=f"Total number of attended events in the selected date range. Previous period: {previous_attended_events_sum}.")
        
        with col4:
            delta_pct = (non_attended_events_sum - previous_non_attended_events_sum) / previous_non_attended_events_sum * 100
            st.metric(label="Non-Attended Events", value=non_attended_events_sum, delta=f"{delta_pct:,.0f}%", help=f"Total number of non-attended events in the selected date range. Previous period: {previous_non_attended_events_sum}.")

    
        # Fetch events
        events = fetch_events(location["lat"], location["lon"], radius, date_from=daterange[0], date_to=daterange[1], categories=selected_categories)
        
        show_map(lat=location["lat"], lon=location["lon"], events=events)


        show_events_list(events)


def calc_sum_of_features(features_result, features):
    # sum up the attendance features
    phq_attendance_sum = 0

    for item in features_result["results"]:
        for k, v in item.items():
            phq_attendance_sum += v["stats"]["sum"] if k in features else 0

    return phq_attendance_sum

def calc_sum_of_event_counts(counts_result, categories):
    counts = {k: v for k, v in counts_result["categories"].items() if k in categories}

    return sum(counts.values())

@st.cache_data
def fetch_suggested_radius(lat, lon, radius_unit="mi", industry="parking"):
    phq = get_predicthq_client()
    suggested_radius = phq.radius.search(location__origin=f"{lat},{lon}", radius_unit=radius_unit, industry=industry)
    
    return suggested_radius.to_dict()

@st.cache_data
def fetch_event_counts(lat, lon, radius, date_from, date_to, radius_unit="mi"):
    phq = get_predicthq_client()
    counts = phq.events.count(
        within=f"{radius}{radius_unit}@{lat},{lon}",
        active={
            "gte": date_from,
            "lte": date_to,
        },
        state="active",
    )

    return counts.to_dict()


@st.cache_data
def fetch_features(lat, lon, radius, date_from, date_to, features=[], radius_unit="mi"):
    phq = get_predicthq_client()
    features = phq.features.obtain_features(
        location__geo={
            "lat": lat,
            "lon": lon,
            "radius": f"{radius}{radius_unit}",
        },
        active={
            "gte": date_from,
            "lte": date_to,
        },
        **{feature: True for feature in features},
    )

    return features.to_dict()


@st.cache_data
def fetch_events(lat, lon, radius, date_from, date_to, categories=[], radius_unit="mi"):
    phq = get_predicthq_client()
    events = phq.events.search(
        within=f"{radius}{radius_unit}@{lat},{lon}",
        active__gte=date_from,
        active__lte=date_to,
        category=",".join(categories),
        state="active",
        limit=100,
        sort="phq_attendance",
    )

    return events.to_dict()



def show_events_list(events):
    results = []

    for event in events["results"]:
        venue = next(filter(lambda entity: entity["type"] == "venue", event["entities"]), None)

        row = {
            "id": event["id"],
            "title": event["title"],
            "phq_attendance": event["phq_attendance"] if event["phq_attendance"] else 0,
            "category": event["category"],
            "start_date": event["start"], # TODO convert from UTC to local
            "end_date": event["end"],
            "predicted_end_date": event["predicted_end"],
            "venue_name": venue["name"] if venue else "",
            "venue_address": venue["formatted_address"] if venue else "",
            "placekey": event["geo"]["placekey"] if "geo" in event and "placekey" in event["geo"] else "",
        }

        results.append(row)

    events_df = pd.DataFrame(results)
    st.dataframe(events_df)

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(events_df)

    st.download_button(
        label="Download events as CSV",
        data=csv,
        file_name='events.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()