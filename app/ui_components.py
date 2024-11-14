import streamlit as st
import streamlit_antd_components as sac
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime, time
def styled_button(label: str, key: str = None) -> bool:
    """
    Display a styled Streamlit button with custom CSS.
    """
    st.markdown("""
        <style>
        div.stButton > button {
            display: block;            
            width: 300px; 
            background-color: #0366d6;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            padding: 12px 12px; 
            border: none; 
        }
        div.stButton > button:hover {
            background-color: #024ea2;
        }
        </style>
    """, unsafe_allow_html=True)
    return st.button(label, key=key)

def date_time_inputs() -> Tuple:
    with st.sidebar:
        with st.expander("Date and Time Filters", True):
            start_dt = st.date_input("Start Date", pd.Timestamp.today() - pd.Timedelta(days=30))
            start_time = st.time_input("Start Time", pd.Timestamp.now().time().replace(hour=0, minute=0, second=0, microsecond=0))
            end_dt = st.date_input("End Date", pd.Timestamp.today())
            end_time = st.time_input("End Time", pd.Timestamp.now().time().replace(hour=23, minute=59, second=59, microsecond=999999))
            
            # Combine the selected date and time
            start_datetime = datetime.combine(start_dt, start_time)
            start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Combine the selected date and time
            end_datetime = datetime.combine(end_dt, end_time)
            end_datetime = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
            
            
    return start_datetime, end_datetime

def drift_type_inputs() -> List[str]:
    with st.sidebar:
        with st.expander("Drift Filters", True):
            data_drift = st.checkbox("Feature Drift", value=True)
            concept_drift = st.checkbox("Concept Drift", value=True)
    return data_drift, concept_drift


def build_tree_structure(df: pd.DataFrame, experiment_name: str) -> Tuple[List[sac.TreeItem], Dict[str, str]]:
    tree_items = []
    label_to_id_mapping = {}

    # Create a list of runs
    run_items = []
    for _, row in df.iterrows():
        run_label = f"Run - {row['created_at']} - {experiment_name} "
        label_to_id_mapping[run_label] = row['id']
        run_items.append(
            sac.TreeItem(
                label=run_label
            )
        )

    # Create the tree item for the experiment
    experiment_label = f"{experiment_name}"
    tree_items.append(
        sac.TreeItem(
            label=experiment_label,
            icon='folder',
            children=run_items
        )
    )

    return tree_items, label_to_id_mapping

def display_tree(tree_items: List[sac.TreeItem]) -> List[str]:
    with st.expander("Drift Treeview", True):
        search_query = st.text_input("Search Runs", "")
        filtered_items = filter_tree_items(tree_items, search_query) if search_query else tree_items
        return sac.tree(items=filtered_items, label='Drift Runs', align='start', size='md', open_all=True, checkbox=True)

def filter_tree_items(items: List[sac.TreeItem], query: str) -> List[sac.TreeItem]:
    filtered_items = []
    for item in items:
        if query.lower() in item.label.lower():
            filtered_items.append(item)
        elif hasattr(item, 'children') and item.children:
            filtered_children = filter_tree_items(item.children, query)
            if filtered_children:
                filtered_items.append(sac.TreeItem(
                    label=item.label, 
                    icon=item.icon, 
                    disabled=item.disabled, 
                    children=filtered_children, 
                    tooltip=item.tooltip
                ))
    return filtered_items

def display_selected_runs(selected_nodes: List[str], df: pd.DataFrame, label_to_id_mapping: Dict[str, str]):
    if selected_nodes:
        # Get the run IDs for the selected nodes using the mapping dictionary
        selected_run_ids = [label_to_id_mapping.get(label) for label in selected_nodes if label in label_to_id_mapping]
        # Filter out None values if any label wasn't found
        selected_run_ids = [run_id for run_id in selected_run_ids if run_id is not None]

        filtered_df = df[df['id'].isin(selected_run_ids)]

        if filtered_df.empty:
            st.info("No runs available for this filter criteria.")
        else:
            st.subheader("Selected Runs")
            st.dataframe(filtered_df.reset_index(drop=True))
            drift_parameters_list, features = extract_drift_run_parameters(filtered_df)
            st.subheader("Drift Graph")
            display_graphs(filtered_df, drift_parameters_list, features)
    else:
        # Show a message if no runs match the selected criteria
        st.info("No run selected, please select a run from the tree.")

def extract_drift_run_parameters(df: pd.DataFrame) -> Tuple[List[Dict], set]:
    drift_parameters_list = []
    features = set()
    for _, row in df.iterrows():
        # Extract parameters from both data_drift and concept_drift
        data_drift_params = row.get("data_drift", {}).get("parameters", {})
        concept_drift_params = row.get("concept_drift", {}).get("parameters", {})
        params = {**data_drift_params, **concept_drift_params}
        drift_parameters_list.append(params)
        features.update(params.keys())
    return drift_parameters_list, features

def display_graphs(df: pd.DataFrame, drift_parameters_list: List[Dict], features: set):
    if features:
        selected_features = st.sidebar.multiselect("Select Features", list(features), default=list(features))
        if selected_features:
            fig, ax = plt.subplots(figsize=(15, 8))
            for feature in selected_features:
                values = [params.get(feature, np.nan) for params in drift_parameters_list]
                ax.scatter(df["created_at"], values, s=50, label=feature)
            ax.set_xlabel("Experiment Date and Time", fontsize=14)
            ax.set_ylabel("Feature Values", fontsize=14)
            ax.legend(title="Features")
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.warning("Please select at least one feature.")
    else:
        st.info("No drift parameters available to display.")

def display_experiment_table(experiments: List[Dict], permissions: Dict[str, bool]):
    st.markdown("<h2 style='text-align: left;'>Completed Jobs</h2>", unsafe_allow_html=True)
    
    # Add margin between the search input and the table header
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
 
    # Consolidated CSS for table with centered header
    st.markdown(
        """
        <style>
        .experiment-table {
            width: 300px; /* Set the width to match buttons */
            border-collapse: collapse;
        }
        .experiment-table th {
            padding: 12px;
            text-align: center; /* Center-align header text */
            background-color: #f5f7fa;
            color: #333;
            font-weight: bold;
        }
        .experiment-table td {
            padding: 12px;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Search functionality
    search_query = st.text_input("Search experiments", "")
    filtered_experiments = [exp for exp in experiments if search_query.lower() in exp.get("name", "").lower()]

    # Add space between search input and table header
    st.markdown(
        """
        <div style="margin-top: 20px;"></div>
        """,
        unsafe_allow_html=True
    )

    # Display the experiments in a table format with a centered header
    st.markdown(
        """
        <table class='experiment-table'>
            <tr><th>All Experiments</th></tr>
        """,
        unsafe_allow_html=True
    )
    
    if not filtered_experiments:
        st.warning('No experiment found')
        
    for exp in filtered_experiments:
        exp_name = exp.get("name", "")
        exp_id = exp.get("id", "")
        
        # Check if the user has permission to view the experiment
        has_permission = permissions.get(exp_id, False)
        
        # Create a unique key for each button
        button_key = f"exp_{exp_id}"
        
        # Display experiment name as a button in table row format
        if styled_button(exp_name, key=button_key):
            # Set query params with experiment ID on button click
            st.session_state.query_params = {"experiment_id": exp_id, "has_permission": has_permission, "exp_name": exp_name}
            st.rerun()
    
    st.markdown("</table>", unsafe_allow_html=True)
