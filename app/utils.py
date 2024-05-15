"""Utility functions for the frontend app."""

from collections import ChainMap

import requests
from app import queries
from app.config import monitoring_url, settings


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
            "id": job.get("id", "Missing ID"),
            "job_status": job.get("job_status", "No status found"),
            "datetime": job.get("datetime", "Missing datetime"),
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
    return [
        {
            "id": job.get("id", "Missing ID"),
            "job_status": job.get("job_status", "No status found"),
            "datetime": job.get("datetime", "Missing datetime"),
            "data_drift": job["data_drift"].get("parameters", None),
            "concept_drift": job["concept_drift"].get("parameters", None),
        }
        for job in response.json()
    ]
