import streamlit as st
from predicthq import Client

def get_api_key():
    # api_key = st.session_state.api_key if "api_key" in st.session_state and len(st.session_state.api_key) > 0 else None
    return st.secrets["api_key"]

def get_predicthq_client():
    api_key = get_api_key()
    phq = Client(access_token=api_key)

    return phq