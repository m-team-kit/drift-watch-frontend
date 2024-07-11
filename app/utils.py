"""Utility functions for the frontend app."""

from collections import ChainMap

import requests
from app import queries
from app.config import monitoring_url, settings
import base64
import json

def fetch_uncompleted(start_datetime, end_datetime):
    """Fetch all uncompleted jobs based on the selected date and time."""
    query_list = [
        queries.datetime(start=start_datetime, end=end_datetime),
        queries.job_status(status=["Running", "Failed"]),
    ]
    response = requests.get(
        f"{monitoring_url}/drift",
        json=dict(ChainMap(*query_list)),
        timeout=settings.DRIFT_MONITOR_TIMEOUT,
    )
    response.raise_for_status()
    
    
    
    return [
        {
            "Experiment_id": job.get("id", "Missing ID"),
            "Job_status": job.get("job_status", "No status found"),
            "Experiment_time": job.get("datetime", "Missing datetime"),
        }
        for job in response.json()
    ]


def fetch_drifts(start_datetime, end_datetime, data=True, concept=True):
    """Fetch all feature drifts based on the selected date and time."""
    query_list = [
        queries.datetime(start=start_datetime, end=end_datetime),
        queries.data_drift(drift=data),
        queries.concept_drift(drift=concept),
        queries.job_status(status="Completed"),
    ]
    response = requests.get(
        f"{monitoring_url}/drift",
        json=dict(ChainMap(*query_list)),
        timeout=settings.DRIFT_MONITOR_TIMEOUT,
    )
    response.raise_for_status()
    

    json_data = json.loads(response.text)
 
    data_array = []    
    for item in json_data:
        data_drift_parameters = item["data_drift"]["parameters"]

        concept_drift_parameters = item["concept_drift"]["parameters"]
        
        # if image exists, extract the encoded image data from the JSON response
        if item['data_drift']['parameters'].get('MMD_statistic_image', None):
            encoded_MMD_statistic_image = item['data_drift']['parameters']['MMD_statistic_image']
            # Decode the base64-encoded image data to binary
            MMD_statistic_image = base64.b64decode(encoded_MMD_statistic_image)

        else:
            MMD_statistic_image = None
        

        # Extract the encoded image data from the JSON response
        if item['data_drift']['parameters'].get('data_distribution_image', None):
            encoded_data_distribution_image = item['data_drift']['parameters']['data_distribution_image']
            # Decode the base64-encoded image data to binary
            data_distribution_image = base64.b64decode(encoded_data_distribution_image)
        else:
            data_distribution_image = None

        data_array.append({
            "drift_run_id": item["id"],
            "Experiment_time": item["datetime"],
            "data_drift": item["data_drift"]["drift"],
            "concept_drift": item["concept_drift"]["drift"],
            "concept_drift_parameters" : concept_drift_parameters,
            "data_drift_parameters": data_drift_parameters,            
            "MMD_statistic_image" : MMD_statistic_image,
            "data_distribution_image": data_distribution_image
    })


    return data_array