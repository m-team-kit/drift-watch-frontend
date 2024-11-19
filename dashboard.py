"""Dashboard for monitoring and managing experiment runs using Streamlit.

This module provides a Streamlit-based web application for displaying the 
status of running or failed jobs, as well as completed experiment runs. It 
interacts with an API to fetch entitlement and experiment data, and allows
users to filter and view detailed information about experiment runs.
"""

import sys
import os

# Add the parent_folder_directory/app to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

import streamlit as st
import datetime
import pandas as pd
from app.api_client import APIClient
from typing import List, Dict, Tuple
from app.permissions import PermissionManager
from app.ui_components import (
    date_time_inputs,
    drift_type_inputs,
    build_tree_structure,
    display_tree,
    display_selected_runs,
    display_experiment_table,
)

# Set the page layout to wide
st.set_page_config(layout="wide")


def initialize_api_client() -> APIClient:
    """
    Initializes the API client with an authorization token.
    If the token is not found in secrets, a default placeholder token is used.

    Returns:
        APIClient: The initialized API client with proper headers.
    """

    # Retrieve the authorization token from Streamlit secrets
    auth_token = st.secrets.get("AUTH_TOKEN", None)
    if not auth_token:
        st.warning("Authorization token not found in secrets, please add the token")

    return APIClient(auth_token)


def fetch_data(api_client: APIClient):
    """
    Fetch the entitlement data and experiment data from the API.

    Args:
        api_client (APIClient): The API client to interact with the API.

    Returns:
        Tuple: Entitlement data and experiment data retrieved from the API.
    """
    entitlements_data = api_client.get_entitlements()
    experiments_data = api_client.get_experiments()
    return entitlements_data, experiments_data


def display_uncompleted_jobs(api_client: APIClient, experiments_data: List[Dict]):
    """
    Display the running or failed jobs for experiments, filtering based on a specified date and time range.

    Args:
        api_client (APIClient): The API client used to fetch experiment run data.
        experiments_data (List[Dict]): A list of experiments to process.
    """
    st.title("Running or Failed Jobs")

    # Display date and time filters
    start_datetime, end_datetime = date_time_inputs()

    experiment_data = []

    if experiments_data:
        # Iterate through each experiment to fetch and filter runs
        for experiment in experiments_data:
            experiment_id = experiment["id"]
            # Fetch runs using the API client
            runs = api_client.get_uncompleted_drift_runs(
                experiment_id, start_datetime, end_datetime
            )

            if not runs:
                continue

            for run in runs:
                # Add experiment_id to each run entry
                run["experiment_id"] = experiment_id
                run["Experiment_name"] = experiment["name"]

            # Add the filtered runs to the main experiment_data list
            experiment_data.extend(runs)

        if experiment_data:
            # Create a DataFrame and filter necessary columns
            df = pd.DataFrame(experiment_data)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

            df["Run_id"] = df["id"]

            df = df.loc[
                :, ["Experiment_name", "Run_id", "created_at", "job_status"]
            ].sort_values(by="created_at", ascending=False)

            st.dataframe(df)

        else:
            st.info("No jobs found within the selected date and time range.")

    else:
        st.info("No jobs found within the selected date and time range.")


def display_completed_experiment(
    api_client: APIClient,
    experiments_data: List[Dict],
    permission_manager: PermissionManager,
):
    """
    Display completed jobs and their corresponding runs, either by showing the experiment list or detailed runs.

    Args:
        api_client (APIClient): The API client to interact with the API.
        experiments_data (List[Dict]): A list of experiments to display.
        permission_manager (PermissionManager): Manages user permissions for accessing experiments.
    """
    query_params = st.session_state.get("query_params", {})
    if "experiment_id" in query_params:
        # If an experiment is selected, display the runs associated with that experiment
        experiment_id = query_params["experiment_id"]
        has_permission = query_params.get("has_permission", False)
        display_experiment_runs(
            api_client, experiments_data, experiment_id, has_permission
        )
    else:
        # If no experiment is selected, display the experiments list with search functionality
        display_experiment_table(experiments_data, permission_manager.permissions)


def display_experiment_runs(
    api_client: APIClient,
    experiments_data: List[Dict],
    experiment_id: str,
    has_permission: bool,
):
    """
    Display the runs for a specific experiment, allowing the user to filter by date and drift type.

    Args:
        api_client (APIClient): The API client used to fetch run data.
        experiments_data (List[Dict]): A list of experiments.
        experiment_id (str): The ID of the experiment for which to display runs.
        has_permission (bool): Whether the user has permission to access the experiment.
    """
    # Display a button to go back to the experiments list
    if st.button("Back to Experiments List"):
        st.session_state.query_params = {}
        st.rerun()

    # Get the experiment data by filtering for the specific experiment ID
    experiment = next(
        (exp for exp in experiments_data if exp["id"] == experiment_id), None
    )
    if not experiment:
        st.error("Experiment not found.")
        return

    # If the user does not have permission to view the experiment, display an error message
    if not has_permission:
        required_entitlements = list(experiment.get("permissions", {}).keys())
        error_message = f"""
        <div style="color: red; background-color: #fdd; padding: 10px; border-radius: 5px;">
            You do not have access to this experiment.<br>You are required to be the part of entitlement/group:<br>{'<br>'.join(required_entitlements)}
        </div>
        """
        st.markdown(error_message, unsafe_allow_html=True)
        return

    st.title(f"Runs for Experiment: {experiment.get('name', 'Unknown')}")

    # Display date and time filters
    start_datetime, end_datetime = date_time_inputs()

    data_drift, concept_drift = drift_type_inputs()

    # Fetch completed runs for the selected experiment using the API client
    runs = api_client.get_completed_drift_runs(
        experiment_id, start_datetime, end_datetime, data_drift, concept_drift
    )

    if not runs:
        st.info("No runs available for this filter criteria.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(runs)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # If no data remains after filtering, display an informational message
    if df.empty:
        st.info("No runs found in the selected date and time range.")
        return

    # Build a tree structure for displaying runs in a hierarchical format
    tree_items, label_to_id_mapping = build_tree_structure(
        df, experiment.get("name", "Name Unknown")
    )

    with st.sidebar:
        # Display the tree of experiment runs in the sidebar
        selected_nodes = display_tree(tree_items)

    # Show a message if no runs exist for the selected criteria
    if not tree_items:
        st.info("No runs exist for this filter.")
        return

    # Display the selected runs based on user choice
    display_selected_runs(selected_nodes, df, label_to_id_mapping)


def main():
    """
    Main function for running the Streamlit application.

    Initializes the API client, fetches the data, and determines which tab is selected by the user.
    Displays either the "Job Status" tab or the "Completed Jobs" tab.
    """
    # Initialize the API client with an authorization token
    api_client = initialize_api_client()

    # Fetch the entitlements and experiment data
    entitlements_data, experiments_data = fetch_data(api_client)

    if entitlements_data:
        # Extract user entitlements from the fetched data
        user_entitlements = entitlements_data.get("items", [])
    else:
        user_entitlements = None

    # Fetch the user data and get the user ID
    user_data = api_client.fetch_json(
        "user/self", {}
    )  # Assuming user/self endpoint returns user info

    if user_data:
        user_id = user_data.get("id", "unknown_user_id")
    else:
        user_id = None

    # Create a PermissionManager instance for managing experiment permissions
    permission_manager = PermissionManager(
        user_id=user_id, entitlements=user_entitlements, experiments=experiments_data
    )

    # Allow the user to select which tab to display
    selected_tab = st.sidebar.radio("Select Tab", ["Job Status", "Completed Jobs"])

    # Display the selected tab's content
    if selected_tab == "Job Status":
        display_uncompleted_jobs(api_client, experiments_data)
    elif selected_tab == "Completed Jobs":
        display_completed_experiment(api_client, experiments_data, permission_manager)


if __name__ == "__main__":
    main()
