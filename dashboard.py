"""Entry point for the Streamlit dashboard."""

import streamlit as st
from app import utils

# Set the page layout to wide
st.set_page_config(layout="wide")


# Define the main function
def main():
    tabs = ["Job Status", "Completed Jobs"]
    selected_tab = st.sidebar.radio("Select Tab", tabs)

    if selected_tab == "Completed Jobs":
        utils.display_data()
    elif selected_tab == "Job Status":
        utils.display_jobs_by_status()


if __name__ == "__main__":
    main()
