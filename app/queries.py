"""Module to define the queries of the frontend application."""


def datetime(start=None, end=None):
    """Return the query for the selected date and time."""
    return {"datetime": {"$gte": start, "$lte": end}}


def job_status(status=None):
    """Return the query for the selected job status."""
    if isinstance(status, list):
        return {"job_status": {"$in": status}}
    return {"job_status": status}


def data_drift(drift=None):
    """Return the query for the selected data drift."""
    return {"data_drift.drift": drift}


def concept_drift(drift=None):
    """Return the query for the selected concept drift."""
    return {"concept_drift.drift": drift}
