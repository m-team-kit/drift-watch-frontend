import requests
from requests.exceptions import RequestException
from collections import ChainMap
from config import settings
import queries  
import streamlit as st

class APIClient:
    """
    A client for interacting with the Drift Watch API.
    
    Attributes:
        base_url (str): Base URL for API endpoints.
        headers (dict): Headers for API requests, including authorization.
    """

    def __init__(self, auth_token: str):
        """Initializes APIClient with the authorization token."""
        self.base_url = settings.base_api_url
        
        self.headers = {
            "Authorization": f"{settings.AUTH_SCHEME} {auth_token}",
            "Content-Type": "application/json"
        }
                
        # self.headers = {
        #     "Content-Type": "application/json"
        # }


    def fetch_json(self, endpoint: str, query_list=[]):
        """
        Sends a GET request to the specified endpoint with the given query list.

        Args:
            endpoint (str): The API endpoint.
            query_list (list): List of query dictionaries to combine.

        Returns:
            dict or None: JSON response if successful; otherwise, None.
        """
        url = f"{self.base_url}/{endpoint}"  
        
        # Append default pagination parameters
        url += f"?page={settings.DEFAULT_PAGE}&page_size={settings.DEFAULT_PAGE_SIZE}"        
              
        query_data = dict(ChainMap(*query_list))  # Combine query dicts
        response = requests.get(url, headers=self.headers, json=query_data, timeout=settings.API_TIMEOUT, verify=False)
        return response.json() if response.status_code == 200 else None


    def fetch_json_via_post(self, endpoint: str, query_list=[]):
        """
        Sends a POST request to the specified endpoint with the given query list.

        Args:
            endpoint (str): The API endpoint.
            query_list (list): List of query dictionaries to combine.

        Returns:
            dict or None: JSON response if successful; otherwise, None.
        """
        url = f"{self.base_url}/{endpoint}"  
        
        # Append default pagination parameters
        url += f"?page={settings.DEFAULT_PAGE}&page_size={settings.DEFAULT_PAGE_SIZE}"        
              
        query_data = dict(ChainMap(*query_list))  # Combine query dicts
        response = requests.post(url, headers=self.headers, json=query_data, timeout=settings.API_TIMEOUT, verify=False)
        
        if response.status_code == 403:
            # Return a specific error message for 403
            return {
                "error": "You do not have permission to access this experiment.",
                "status_code": 404,
                "details": response.text
            }
            
        elif response.status_code == 200:
            # Return JSON response for success
            return response.json()
            
    
    def get_entitlements(self):
        """Fetches user entitlements."""
        return self.fetch_json("entitlement", query_list=[])

    def get_experiments(self, search_text=""):
        """Fetches available experiments."""
        query_list = [{
                "name": {
                        "$regex": search_text,
                        "$options": "i"
            }
        }]
        return self.fetch_json_via_post("experiment/search", query_list)

    def get_uncompleted_drift_runs(self, experiment_id: str, start_datetime, end_datetime):
        """
        Fetches uncompleted drift runs for a specific experiment.

        Args:
            experiment_id (str): The experiment ID.
            start_datetime, end_datetime: Date range for the query.

        Returns:
            dict or None: JSON response with uncompleted runs.
        """
        query_list = [
            queries.datetime(start=start_datetime, end=end_datetime),
            queries.job_status(status=["Running", "Failed"])
        ]
        endpoint = f"experiment/{experiment_id}/drift"
        return self.fetch_json(endpoint, query_list)


    
    def get_completed_drift_runs(self, experiment_id: str, start_datetime, end_datetime):
        """
        Fetches completed drift runs for a specific experiment.

        Args:
            experiment_id (str): The experiment ID.
            start_datetime, end_datetime: Date range for the query.
            data_drift, concept_drift (bool): Filters for drift types.

        Returns:
            dict or None: JSON response with completed runs.
        """
        
        
        query_list = [
            queries.datetime(start=start_datetime, end=end_datetime),
            queries.job_status(status="Completed")
        ]
        
       
                
        endpoint = f"experiment/{experiment_id}/drift/search"        
        
        try:
            return self.fetch_json_via_post(endpoint, query_list)
        except Exception as e:
            if hasattr(e, "status_code") and e.status_code == 404:
                return {"error": "You do not have permission to access this experiment."}
