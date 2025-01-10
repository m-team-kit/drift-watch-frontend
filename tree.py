import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
import datetime

# Set the page layout to wide
st.set_page_config(layout="wide")

# Dummy function to simulate fetching JSON data from an API
import requests  # Make sure to import requests

import requests  # Import requests for API calls

# Dummy function to simulate fetching JSON data from an API
def fetch_json(url):
    # Instead of fetching from an API, return hardcoded data for testing
    if "test-users.json" in url:
        return [
            {"_id": "00000000-0000-0003-0001-000000000001", "created_at": "2021-01-01T00:00:00Z",
             "subject": "user_1", "issuer": "issuer.1", "email": "user_1@issuer.1.com"},
            {"_id": "00000000-0000-0003-0001-000000000002", "created_at": "2021-01-02T00:00:00Z",
             "subject": "user_2", "issuer": "issuer.1", "email": "user_2@issuer.1.com"},
            {"_id": "00000000-0000-0003-0001-000000000003", "created_at": "2021-01-03T00:00:00Z",
             "subject": "user_3", "issuer": "issuer.1", "email": "user_3@issuer.1.com"}
        ]
    elif "test-groups.json" in url:
        return [
            {"_id": "00000000-0000-0002-0001-000000000001", "created_at": "2021-01-01T00:00:00Z", "name": "group_1",
             "members": [
                 "00000000-0000-0003-0001-000000000001",
                 "00000000-0000-0003-0001-000000000002",
                 "00000000-0000-0003-0001-000000000003"
             ]},
            {"_id": "00000000-0000-0002-0001-000000000002", "created_at": "2021-01-02T00:00:00Z", "name": "group_2",
             "members": [
                 "00000000-0000-0003-0001-000000000001",
                 "00000000-0000-0003-0001-000000000002"
             ]},
            {"_id": "00000000-0000-0002-0001-000000000003", "created_at": "2021-01-03T00:00:00Z", "name": "group_3",
             "members": []},
            {"_id": "00000000-0000-0002-0001-000000000004", "created_at": "2021-01-04T00:00:00Z", "name": "group_4",
             "members": []}
        ]
    elif "test-experiments.json" in url:
        return [
            {"_id": "EXP123", "created_at": "2021-01-01T00:00:00Z", "name": "Experiment A",
             "permissions": {
                 "00000000-0000-0002-0001-000000000001": "Manage",
                 "00000000-0000-0002-0001-000000000002": "Edit",
                 "00000000-0000-0002-0001-000000000003": "Read"
             }},
            {"_id": "EXP124", "created_at": "2021-01-02T00:00:00Z", "name": "Experiment B",
             "permissions": {
                 "00000000-0000-0002-0001-000000000002": "Edit",
                 "00000000-0000-0002-0001-000000000003": "Read"
             }},
            {"_id": "EXP125", "created_at": "2021-01-03T00:00:00Z", "name": "Experiment C",
             "permissions": {
                 "00000000-0000-0002-0001-000000000003": "Read"
             }}
        ]
    return []


# Example usage of URLs
USERS_API_URL = "test-users.json"
GROUPS_API_URL = "test-groups.json"
EXPERIMENTS_API_URL = "test-experiments.json"

# Fetch the dummy data using the function
users_data = fetch_json(USERS_API_URL)
groups_data = fetch_json(GROUPS_API_URL)
experiments_data = fetch_json(EXPERIMENTS_API_URL)

# Assume logged-in user is user_1
LOGGED_IN_USER_ID = "00000000-0000-0003-0001-000000000001"

# Function to get groups for the logged-in user
def get_user_groups(user_id, groups_data):
    user_groups = []
    for group in groups_data:
        if user_id in group["members"]:
            user_groups.append(group["_id"])
    return user_groups

# Function to get experiments with permission for the logged-in user's groups
def get_user_experiments_permissions(user_groups, experiments_data):
    experiment_permissions = {}
    for experiment in experiments_data:
        # Check if any group has permissions for the experiment
        has_permission = any(group_id in experiment["permissions"] for group_id in user_groups)
        experiment_permissions[experiment["_id"]] = has_permission
    return experiment_permissions

# Define the tabs for the dashboard
tabs = ["Job Status", "Completed Jobs"]

# Main function for the Streamlit dashboard
def main():
    """Main function for the Streamlit dashboard."""
    selected_tab = st.sidebar.radio("Select Tab", tabs)
    if selected_tab == "Job Status":
        display_jobs_status()
    elif selected_tab == "Completed Jobs":
        display_completed_jobs()
    else:
        st.error(f"Invalid tab {selected_tab}")

# Display jobs status function
def display_jobs_status():
    """Display the running or failed jobs."""
    st.title("Running or Failed Jobs")

    # Simulated start and end date input
    start_dt = st.sidebar.date_input("Start Date")
    start_time = st.sidebar.time_input("Start Time", datetime.time(0, 0))
    end_dt = st.sidebar.date_input("End Date")
    end_time = st.sidebar.time_input("End Time", datetime.time(23, 59))

    # Combine date and time into datetime objects
    start_datetime = datetime.datetime.combine(start_dt, start_time)
    end_datetime = datetime.datetime.combine(end_dt, end_time)

    # Simulated job data
    jobs = [
        {"Experiment_time": "2024-11-01 10:00:00", "Job_status": "Running", "Experiment_id": "EXP123"},
        {"Experiment_time": "2024-10-30 14:30:00", "Job_status": "Failed", "Experiment_id": "EXP124"},
        {"Experiment_time": "2024-10-25 09:15:00", "Job_status": "Running", "Experiment_id": "EXP125"},
    ]

    # Convert to DataFrame
    df = pd.DataFrame(jobs)
    df['Experiment_time'] = pd.to_datetime(df['Experiment_time'])

    # Filter data based on selected date and time range
    mask = (df['Experiment_time'] >= start_datetime) & (df['Experiment_time'] <= end_datetime)
    df = df.loc[mask]

    if df.empty:
        st.info("No jobs match the selected date and time range.")
    else:
        columns = ["Experiment_time", "Job_status", "Experiment_id"]
        st.dataframe(df[columns].sort_values(by="Experiment_time", ascending=False))

# Function to filter tree items based on search query
def filter_tree_items(items, query):
    filtered_items = []
    for item in items:
        if query.lower() in item.label.lower():
            filtered_items.append(item)
        elif hasattr(item, 'children') and item.children:
            filtered_children = filter_tree_items(item.children, query)
            if filtered_children:
                # Create a new TreeItem with filtered children
                new_item = sac.TreeItem(
                    label=item.label,
                    icon=item.icon,
                    tag=item.tag,
                    description=item.description,
                    tooltip=item.tooltip,
                    disabled=item.disabled,
                    children=filtered_children,
                )
                filtered_items.append(new_item)
    return filtered_items

def display_completed_jobs():
    """Display the completed jobs and generate graphs based on their parameters/features."""
    st.title("Completed Jobs")
    st.sidebar.header("Select Filters")

    # Simulated start and end date input
    start_dt = st.sidebar.date_input("Start Date")
    start_time = st.sidebar.time_input("Start Time", datetime.time(0, 0))
    end_dt = st.sidebar.date_input("End Date")
    end_time = st.sidebar.time_input("End Time", datetime.time(23, 59))

    # Combine date and time into datetime objects
    start_datetime = datetime.datetime.combine(start_dt, start_time)
    end_datetime = datetime.datetime.combine(end_dt, end_time)

    # Sidebar options for filtering
    st.sidebar.subheader("Types of Drift")
    data_drift = st.sidebar.checkbox("Feature Drift", value=True)
    concept_drift = st.sidebar.checkbox("Concept Drift", value=True)

    # Determine drift types to filter
    if data_drift and concept_drift:
        drift_types = ["Feature Drift", "Concept Drift", "Both"]
    elif data_drift:
        drift_types = ["Feature Drift"]
    elif concept_drift:
        drift_types = ["Concept Drift"]
    else:
        drift_types = ["None"]

    # Simulated job data
    jobs = [
        {"experiment_name": "Experiment A", "run_name": "Run 1", "drift_run_id": "RUN001", "experiment_id": "EXP123",
         "Experiment_time": "2024-10-20 08:00:00", "data_drift": True, "concept_drift": False},
        {"experiment_name": "Experiment A", "run_name": "Run 2", "drift_run_id": "RUN002", "experiment_id": "EXP123",
         "Experiment_time": "2024-10-21 14:30:00", "data_drift": False, "concept_drift": True},
        {"experiment_name": "Experiment B", "run_name": "Run 1", "drift_run_id": "RUN003", "experiment_id": "EXP124",
         "Experiment_time": "2024-10-22 09:45:00", "data_drift": True, "concept_drift": True},
        {"experiment_name": "Experiment C", "run_name": "Run 1", "drift_run_id": "RUN004", "experiment_id": "EXP125",
         "Experiment_time": "2024-11-01 11:15:00", "data_drift": False, "concept_drift": False},
        # Additional runs
        {"experiment_name": "Experiment A", "run_name": "Run 3", "drift_run_id": "RUN005", "experiment_id": "EXP123",
         "Experiment_time": "2024-10-23 16:00:00", "data_drift": True, "concept_drift": True},
        {"experiment_name": "Experiment B", "run_name": "Run 2", "drift_run_id": "RUN006", "experiment_id": "EXP124",
         "Experiment_time": "2024-10-24 10:30:00", "data_drift": False, "concept_drift": True},
        {"experiment_name": "Experiment C", "run_name": "Run 2", "drift_run_id": "RUN007", "experiment_id": "EXP125",
         "Experiment_time": "2024-10-25 14:00:00", "data_drift": True, "concept_drift": False},
    ]

    # Convert jobs to DataFrame
    df = pd.DataFrame(jobs)
    df['Experiment_time'] = pd.to_datetime(df['Experiment_time'])

    # Filter data based on selected date and time range
    mask = (df['Experiment_time'] >= start_datetime) & (df['Experiment_time'] <= end_datetime)
    df = df.loc[mask]

    # Filter data based on drift types
    df['Drift_Type'] = df.apply(determine_drift_type, axis=1)
    df = df[df['Drift_Type'].isin(drift_types)]

    if df.empty:
        st.info("No experiments match the selected filters.")
        return

    # Get groups for the logged-in user
    user_groups = get_user_groups(LOGGED_IN_USER_ID, groups_data)

    # Get experiments with permission for the user's groups
    experiment_permissions = get_user_experiments_permissions(user_groups, experiments_data)

    # Build the tree structure
    tree_items = build_tree_structure(df, experiment_permissions)

    # Sidebar for search functionality and tree
    with st.sidebar:
        st.header("Search Experiments")
        search_query = st.text_input("Search experiments or runs", "")
        filtered_tree_items = filter_tree_items(tree_items, search_query) if search_query else tree_items

        # Display the tree and capture selected nodes
        selected_nodes = sac.tree(
            items=filtered_tree_items,
            label='Drift Experiments',
            align='start',
            size='md',
            open_all=True,
            checkbox=True,
        )

    # Check if selected nodes are runs, not experiments
    if selected_nodes:
        # Filter out only the nodes that correspond to runs
        selected_run_ids = [
            label.split(' ')[1].strip('()')
            for label in selected_nodes
            if "Run" in label  # Check if the label indicates a run
        ]

        if selected_run_ids:
            # Filter the DataFrame to show only selected runs
            filtered_df = df[df['drift_run_id'].isin(selected_run_ids)]

            # Display the filtered DataFrame
            st.subheader("Selected Runs")
            st.dataframe(filtered_df.reset_index(drop=True))
        else:
            st.warning("No runs selected. Please select a run from the tree.")
    else:
        st.warning("No runs selected. Please select a run from the tree.")

def determine_drift_type(row):
    if row.get('data_drift') and row.get('concept_drift'):
        return "Both"
    elif row.get('data_drift'):
        return "Feature Drift"
    elif row.get('concept_drift'):
        return "Concept Drift"
    else:
        return "None"

def build_tree_structure(df, experiment_permissions):
    experiments = df['experiment_name'].unique()
    tree_items = []
    for experiment in experiments:
        experiment_runs = df[df['experiment_name'] == experiment]
        experiment_id = experiment_runs.iloc[0]['experiment_id']

        # Check permission to enable or disable
        is_disabled = not experiment_permissions.get(experiment_id, False)

        # Only include runs if the experiment is enabled
        run_items = []
        if not is_disabled:
            for _, row in experiment_runs.iterrows():
                run_label = f"Run {row['drift_run_id']} ({row['Experiment_time'].strftime('%Y-%m-%d %H:%M')})"
                run_item = sac.TreeItem(
                    label=run_label,
                )
                run_items.append(run_item)

        # Tooltip message for disabled experiments
        tooltip_message = "You do not have permission to access this experiment." if is_disabled else None

        experiment_item = sac.TreeItem(
            label=experiment,
            icon='folder',
            disabled=is_disabled,
            tooltip=tooltip_message,  # Add tooltip here
            children=run_items if not is_disabled else None
        )
        tree_items.append(experiment_item)
    return tree_items


if __name__ == "__main__":
    main()
