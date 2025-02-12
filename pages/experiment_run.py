import streamlit as st
from app.api_client import APIClient
from app.ui_components import (    
    date_time_inputs,
    tags_type_inputs,    
    display_selected_runs)


import streamlit as st

   
import pandas as pd
# Page config
st.set_page_config(
    page_title="Experiment Runs",
    page_icon="🔍",
    layout="wide"
)

def display_experiment_runs(api_client: APIClient,  experiment_id: str):
    """
    Display the runs for a specific experiment, allowing the user to filter by date and drift type.
    
    Args:
        api_client (APIClient): The API client used to fetch run data.
        experiments_data (List[Dict]): A list of experiments.        
        experiment_id (str): The ID of the experiment for which to display runs.
        has_permission (bool): Whether the user has permission to access the experiment.
    """
    
    with st.sidebar:
        with st.expander("Job type filters", expanded=True):
            run_type = st.selectbox(
            "Select Run Type",
            ["Completed jobs", "Running jobs", "Failed jobs"]
        )
            
        
    # Display a button to go back to the experiments list
    if st.button("Back to Experiments List"):
        st.query_params = {}
        st.switch_page("experiments.py")

        st.rerun()

    
    # Display date and time filters
    start_datetime, end_datetime = date_time_inputs()


    
    experiments_name = api_client.get_experiment(experiment_id)

    st.header(f"Experiment Runs for {experiments_name}")
    
    
    # Filter and sort df based on selections
    if run_type == "Completed jobs":
        status = 'Completed'
    elif run_type == "Failed jobs":
        status =  'Failed'
    elif run_type == "Running jobs":
        status   = 'Running'

    
    # Fetch completed runs for the selected experiment using the API client
    runs = api_client.get_drift_runs(experiment_id, start_datetime, end_datetime, status)
        
    if isinstance(runs, dict) and 'error' in runs:
        if runs["error"]:
                st.error("You do not have permission to access this experiment.")
                return
                        
    if not runs:
        st.info("No runs available for this filter criteria.")
        return
    
    tags_list = set(tag for run in runs for tag in run['tags'])
    
  
    selected_tags = tags_type_inputs(tags_list)
    
    # Convert to DataFrame
    df = pd.DataFrame(runs)    
    
    
    df = df[df['tags'].apply(lambda x: any(tag in selected_tags for tag in x))]


    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime("%Y-%m-%dT%H:%M:%S")

    
    # If no data remains after filtering, display an informational message
    if df.empty:
        st.info("No runs found in the selected date and time range.")
        return

    checkbox_states = {}

      
    
    with st.sidebar:
        
        # Create mapping of labels to run IDs first
        label_to_id_mapping = {}
        for _, row in df.iterrows():
            run_label = f"Run - {row['created_at']}"
            label_to_id_mapping[run_label] = row['id']

        # Filter runs based on search if needed
        search_query = st.text_input("Search Runs", "")
        filtered_runs = {
            label: run_id 
            for label, run_id in label_to_id_mapping.items() 
            if search_query.lower() in label.lower() or not search_query
        }

        # Initialize select_all in session state
        if 'select_all' not in st.session_state:
            st.session_state.select_all = True

      
        st.title("Select Options")
        # Select All checkbox
        select_all = st.checkbox("Select All", value=st.session_state.select_all)

            

        # Filter df based on status before creating label_to_id_mapping
        df = df[df['job_status'] == 'completed' if run_type == "Completed Runs" else df['job_status'] != 'completed']

        if select_all:
            st.session_state.selected_runs = list(filtered_runs.values())
        else:
            st.session_state.selected_runs = []
        
        # Handle select all changes
        if select_all != st.session_state.select_all:
            st.session_state.select_all = select_all
           
            st.rerun()


        # Display filtered runs
        for label, run_id in filtered_runs.items():
            checkbox_states[run_id] = st.checkbox(label, key=f"run_{run_id}", 
                       value=run_id in st.session_state.get('selected_runs', []))
            
        

    # Show a message if no runs exist for the selected criteria
    if not checkbox_states:
        st.info("No runs exist for this filter.")
        return

    # Get the selected checkboxes (True values)
    selected_values = [checkbox_id for checkbox_id, checkbox in checkbox_states.items() if checkbox]

    
    # Display the selected runs based on user choice
    display_selected_runs(selected_values, df, label_to_id_mapping)



experiment_id = st.session_state.get("query_params", {}).get("experiment_id", None)

st.write(f"Experiment ID: {experiment_id}")

if experiment_id:
    
    # Retrieve the authorization token from Streamlit secrets
    auth_token = st.secrets.get("AUTH_TOKEN", None)
    if not auth_token:
        st.warning("Authorization token not found in secrets, please add the token")
    
    api_client =  APIClient(auth_token)
    
    display_experiment_runs(api_client, experiment_id)
else:
    st.error("No experiment ID provided")
    

