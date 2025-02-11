import sys
import os

# Add the parent_folder_directory/app to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  'app')))

import streamlit as st
import pandas as pd
from app.api_client import APIClient
from typing import List, Dict
from app.ui_components import (    
    display_experiment_table
)

# Set the page layout to wide
st.set_page_config(layout="wide")

def get_api_client() -> APIClient:
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


def display_all_experiments(api_client: APIClient, experiments_data: List[Dict]):
    """
    Display completed jobs and their corresponding runs, either by showing the experiment list or detailed runs.
    
    Args:
        api_client (APIClient): The API client to interact with the API.
        experiments_data (List[Dict]): A list of experiments to display.
        permission_manager (PermissionManager): Manages user permissions for accessing experiments.
    # """



def main():
    """
    Main function for running the Streamlit application.
    
    Initializes the API client, fetches the data, and determines which tab is selected by the user.
    Displays either the "Job Status" tab or the "All Experiments" tab.
    """
    # Initialize the API client with an authorization token
    api_client = get_api_client()

    # Fetch the entitlements and experiment data
    experiments_data = fetch_data(api_client)

        
    display_experiment_table(experiments_data, api_client)
    
if __name__ == "__main__":
    main()
