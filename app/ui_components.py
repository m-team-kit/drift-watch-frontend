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
        params = row.get("parameters", {})
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
from typing import List, Dict
import pandas as pd
import streamlit as st
from typing import List, Dict
import pandas as pd
import streamlit as st

import streamlit as st
import pandas as pd
from typing import List, Dict
import streamlit as st
import pandas as pd
from typing import List, Dict

def display_experiment_table(experiments: List[Dict], api_client):
    # Inject custom CSS for table borders
    # Inject custom CSS for table borders

    # Inject custom CSS for table borders with column separators
    # Inject custom CSS for table borders with column separators
    st.markdown("""
    <style>
    .table-container {
        width: 100%;
        border-collapse: collapse;
    }
    .table-header, .table-row {
        display: grid;
        grid-template-columns: 2fr 4fr 3fr 1fr; /* Adjust column widths */
        width: 100%;
        border: 1px solid #ddd;
    }
    .table-header div, .table-row div {
        padding: 8px;
        border-right: 1px solid #ddd; /* Add column separator */
        text-align: left;
    }
    .table-header div:last-child, .table-row div:last-child {
        border-right: none; /* Remove the right border for the last column */
    }
    .table-header {
        background-color: #f2f2f2;
        font-weight: bold;
        border-bottom: 2px solid #ddd; /* Distinct bottom border for the header */
    }
    .table-row {
        background-color: #fff;
    }
    .table-row:hover {
        background-color: #f9f9f9; /* Add hover effect for rows */
    }
    </style>
    """, unsafe_allow_html=True)



    st.markdown("<h2 style='text-align: left;'>Completed Jobs</h2>", unsafe_allow_html=True)

    # Search functionality
    search_text = st.text_input("Search experiments", "")

    # Fetch filtered experiments
    experiments = api_client.get_experiments(search_text)

    # Handle pagination initialization
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # Define pagination settings
    items_per_page = 5
    total_pages = len(experiments) // items_per_page + (len(experiments) % items_per_page > 0)

    # Calculate start and end indices for the current page
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Get current page data
    current_page_experiments = experiments[start_idx:end_idx]

    if current_page_experiments:
        # Table Container
        with st.container():
            # Display table headers
            st.markdown('<div class="table-header">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([2, 4, 3, 1])
            with col1:
                st.markdown("**Name**")
            with col2:
                st.markdown("**Description**")
            with col3:
                st.markdown("**Created At**")
            with col4:
                st.markdown("**Select**")
            st.markdown('</div>', unsafe_allow_html=True)

            # Display each experiment row
            for experiment in current_page_experiments:
                st.markdown('<div class="table-row">', unsafe_allow_html=True)
                row1, row2, row3, row4 = st.columns([2, 4, 3, 1])

                # Name with clickable link
                experiment_name = f"{experiment['name']}"
                row1.markdown(experiment_name, unsafe_allow_html=True)

                # Description
                row2.markdown(experiment.get('description', 'N/A'))

                # Created At
                row3.markdown(experiment.get('created_at', 'N/A'))

                # Select Button
                select_key = f"select_{experiment['id']}"
                if row4.button("Select", key=select_key):
                    st.session_state["query_params"] = {"experiment_id": experiment['id']}
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # Optional: Display selected experiment
        query_params = st.session_state.get("query_params", {})
        if "experiment_id" in query_params:
            experiment_id = query_params["experiment_id"]
            st.success(f"Selected Experiment ID: {experiment_id}")
           
    else:
        st.warning("No experiments found")

    # Pagination controls
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("Previous") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()
    with col_next:
        if st.button("Next") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.rerun()

    # Display current page info in the center column
    with col_info:
        st.write(f"Page {st.session_state.current_page} of {total_pages}")
        st.write(f"Showing {len(current_page_experiments)} items out of {len(experiments)} total.")

