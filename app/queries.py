"""Module to define the queries of the frontend application."""


def datetime(start=None, end=None):
    """Return the query for the selected date and time."""
    return {"created_at": {"$gte": start, "$lte": end}}


def job_status(status=None):
    """Return the query for the selected job status."""
    if isinstance(status, list):
        return {"job_status": {"$in": status}}
    return {"job_status": status}


def tags_contains(tags=None):
    """Construct the query to check if 'tags' field contains any of the specified value."""
    if not isinstance(tags, list):
        return {"tags" : {"$in": tags}}
    return {"tags" : tags} 


def experiment_id(experiment_id=None):
    """Construct the query to find experiment coressponding to the experiment_id."""
    return {"id" : f"{experiment_id}"} 