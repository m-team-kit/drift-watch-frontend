"""Module to define the components of the frontend application."""

from datetime import datetime, time

import streamlit as st


def add_start_date():
    """Add the start date to the Streamlit app."""

    # Select Start Date
    start_date = st.date_input(
        "Select Start Date",
        min_value=datetime(2021, 1, 1),
        max_value=None,
    )

    # Select Start Time
    start_time = st.time_input(
        "Select Start Time",
        value=time(0, 0, 0),
    )

    # Combine the selected date and time
    dt = datetime.combine(start_date, start_time)
    dt = dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Return dt to keep in main function memory
    return dt


def add_end_date():
    """Add the end date to the Streamlit app."""

    # Select End Date
    end_date = st.date_input(
        "Select End Date",
        min_value=datetime(2021, 1, 1),
        max_value=None,
    )

    # Select End Time
    end_time = st.time_input(
        "Select End Time",
        value=time(23, 59, 59),
    )

    # Combine the selected date and time
    dt = datetime.combine(end_date, end_time)
    dt = dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Return dt to keep in main function memory
    return dt
