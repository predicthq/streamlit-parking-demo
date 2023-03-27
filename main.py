import streamlit as st
from utils.sidebar import show_sidebar_options
from utils.pages import set_page_config
from pathlib import Path

def main():
    set_page_config("Parking Demo App")
    show_sidebar_options()

    # Render the readme as markdown using st.markdown.
    txt = Path("docs/main.md").read_text()
    st.markdown(txt)


if __name__ == "__main__":
    main()