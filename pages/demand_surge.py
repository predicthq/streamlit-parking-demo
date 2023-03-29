import streamlit as st
from utils.pages import set_page_config
from utils.sidebar import show_sidebar_options
from utils.predicthq import get_api_key

def main():
    set_page_config("Demand Surge")
    show_sidebar_options()

    if get_api_key() is not None:
        demand_surge()
    else:
        st.warning("Please set a [PredictHQ API Token](https://docs.predicthq.com/oauth2/introduction).", icon="⚠️")

def demand_surge():
    st.header("Demand Surge")
    st.markdown("(TODO)")

if __name__ == "__main__":
    main()