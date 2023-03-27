import streamlit as st
import datetime
from utils.predicthq import get_api_key

def show_sidebar_options():
    # Prepare the PredictHQ API Key which is required to run the app
    api_key = st.session_state.api_key if "api_key" in st.session_state else ""
    st.sidebar.text_input("PredictHQ API Token", value=api_key, help="A [PredictHQ API Token](https://docs.predicthq.com/oauth2/introduction) is required to run the app.", key="api_key")

    locations = [
        {
            "id": "san-francisco",
            "name": "San Francisco",
            "lat": 37.78690,
            "lon": -122.40152
        },
        {
            "id": "new-york",
            "name": "New York",
            "lat": 40.71,
            "lon": -74.01
        },
        {
            "id": "los-angeles",
            "name": "Los Angeles",
            "lat": 34.05,
            "lon": -118.24
        }
    ]

    index = locations.index(st.session_state.location) if "location" in st.session_state else 0
    st.sidebar.selectbox("Parking Building", locations, index=index, format_func=lambda x: x["name"], help="Select the fictional parking building location.", disabled=get_api_key() is None, key="location")

    # Prepare the date range (today + 30d as the default)
    today = datetime.date.today()
    date_options = [
        {
            "name": "Next 7 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=7)
        },
        {
            "name": "Next 30 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=30)
        },
        {
            "name": "Next 90 days",
            "date_from": today,
            "date_to": today + datetime.timedelta(days=90)
        }
    ]

    index = date_options.index(st.session_state.daterange) if "daterange" in st.session_state else 0
    st.sidebar.selectbox("Date Range", date_options, index=index, format_func=lambda x: x["name"], help="Select the date range for fetching event data.", disabled=get_api_key() is None, key="daterange")


    

    