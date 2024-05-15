"""Entry point for the Streamlit dashboard."""

import pandas as pd
import streamlit as st
from app import components, utils

# Set the page layout to wide
st.set_page_config(layout="wide")

# Define the tabs for the dashboard
tabs = ["Job Status", "Completed Jobs"]


# Main function for the Streamlit dashboard
def main():
    """Main function for the Streamlit dashboard."""
    match st.sidebar.radio("Select Tab", tabs):
        case "Job Status":
            display_jobs_status()
        case "Completed Jobs":
            display_completed_jobs()
        case _tab:
            raise RuntimeError(f"Invalid tab {_tab}")


def display_jobs_status():
    """Display the running or failed jobs."""
    st.title("Running or Failed jobs")

    # Add the start and end date components
    start_dt = components.add_start_date()
    end_dt = components.add_end_date()

    # Fetch the uncompleted jobs based on the selected date and time
    jobs = utils.fetch_uncompleted(start_dt, end_dt)
    if not jobs:
        st.info("No running or failed jobs found.")
        return

    # Display the jobs in a DataFrame
    df = pd.DataFrame(jobs).sort_values(by="datetime", ascending=False)
    columns = ["datetime", "job_status", "id"]
    st.dataframe(df[columns])


# Define the drift filter options for the completed tab
drift_options = ["Feature Drift", "Concept Drift", "No Drift Detected"]


def display_completed_jobs():
    """Display the completed jobs."""
    st.title("Completed jobs")

    # Add the start and end date components
    start_dt = components.add_start_date()
    end_dt = components.add_end_date()

    # Set feature_drift and concept_drift for filtering
    data = st.sidebar.checkbox("Feature Drift", value=True)
    concept = st.sidebar.checkbox("Concept Drift", value=True)

    # Fetch the completed jobs based on the selected date and time
    jobs = utils.fetch_drifts(start_dt, end_dt, data, concept)
    if not jobs:
        st.info("No running or failed jobs found.")
        return

    # Display the jobs in a DataFrame
    df = pd.DataFrame(jobs).sort_values(by="datetime", ascending=False)
    columns = ["datetime", "job_status", "id", "data_drift", "concept_drift"]
    st.dataframe(df[columns])


if __name__ == "__main__":
    main()
