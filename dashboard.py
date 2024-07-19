import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add the parent_folder_directory/app to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  'app')))

# Assuming components and utils are modules with necessary methods
import components
import utils

# Set the page layout to wide
st.set_page_config(layout="wide")

# Define the tabs for the dashboard
tabs = ["Job Status", "Completed Jobs"]

def display_completed_jobs():
    """Display the completed jobs and generate graphs based on their drift parameters"""
    st.title("Completed jobs")

    start_dt, end_dt, data_drift, concept_drift = get_filters_for_completed_jobs()
    jobs = fetch_completed_jobs(start_dt, end_dt, data_drift, concept_drift)

    if jobs.empty:
        st.info("No completed jobs found.")
        return

    display_jobs(jobs, data_drift, concept_drift)
    drift_parameters, features = extract_drift_run_parameters(jobs)
    display_graphs(jobs, drift_parameters, features, data_drift, concept_drift)
    display_experiment_images(jobs)

def get_filters_for_completed_jobs():
    """Get filters for fetching the jobs"""
    start_dt = components.add_start_date()
    end_dt = components.add_end_date()
    data_drift = st.sidebar.checkbox("Data Drift", value=True)
    concept_drift = st.sidebar.checkbox("Concept Drift", value=True)
    return start_dt, end_dt, data_drift, concept_drift

def fetch_completed_jobs(start_dt, end_dt, data_drift, concept_drift):
    """Fetch jobs according to the filter values"""
    jobs = utils.fetch_drifts(start_dt, end_dt, data_drift, concept_drift)
    if jobs:
        return pd.DataFrame(jobs).sort_values(by="Experiment_time", ascending=False)
    return pd.DataFrame()

def display_jobs(jobs, data_drift, concept_drift):
    """Display jobs dataframe with appropriate columns"""

    columns, _ = get_columns_and_title(data_drift, concept_drift)
    st.dataframe(jobs[columns])

def get_columns_and_title(data_drift, concept_drift):
    """Determine columns and title based on drift type"""
    columns = ["drift_run_id", "Experiment_time", "concept_drift",  "concept_drift_parameters", "data_drift", "data_drift_parameters"]
    if concept_drift and data_drift:
        graph_title = "both concept and data drift over time"
    elif concept_drift:
        graph_title = "concept drift over time"
    elif data_drift:
        graph_title = "data drift over time"
    else:
        graph_title = "no drift over time"
    return columns, graph_title

def extract_drift_run_parameters(jobs):
    """Extract drift parameters information from jobs; except images (data_distribution_image, MMD_statistic_image)"""
    feature_drift_list = []
    features = set()
    for _, item in jobs.iterrows():
        feature_drift_dict = {}
        for key, value in item.get("data_drift_parameters", {}).items():
            if key not in ["data_distribution_image", "MMD_statistic_image"]:
                feature_drift_dict[key] = value
                features.add(key)
        for key, value in item.get("concept_drift_parameters", {}).items():
            if key not in ["data_distribution_image", "MMD_statistic_image"]:
                feature_drift_dict[key] = value
                features.add(key)
        feature_drift_list.append(feature_drift_dict)
    return feature_drift_list, features

def display_graphs(jobs, feature_drift_list, features, data_drift, concept_drift):
    """Display graphs for the selected features"""
    if not jobs.empty:
        selected_features = st.sidebar.multiselect("Select Features", list(features), default=list(features))
        if selected_features:
            fig, ax = plt.subplots(figsize=(15, 8))
            for feature in selected_features:
                color = np.random.rand(3,)
                ax.scatter(jobs["Experiment_time"], [item.get(feature, None) for item in feature_drift_list], label=feature, color=color)
            ax.set_xlabel("Experiment Date")
            ax.set_ylabel("Feature Values")
            ax.set_title(get_columns_and_title(data_drift, concept_drift)[1])
            ax.legend(title="Features", loc="upper left")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.warning("Please select at least one feature.")

def display_experiment_images(jobs):
    """Display the images for the last 5 experiments"""
    for index, item in jobs.iloc[-5:, :].iterrows():             
        st.write("\n\n\n\n\n\n")
        if item.get("data_distribution_image", None):
            st.write(f"<p style='text-align:center; font-weight:bold; font-size:16px;'>Data Distribution Graph for: {item['Experiment_time']}</p>", unsafe_allow_html=True)
            st.image(item["data_distribution_image"], caption="data_distribution_image", use_column_width=True)
        if item.get("MMD_statistic_image", None):
            st.write(f"<p style='text-align:center; font-weight:bold; font-size:16px;'>MMD_statistics Graph for {item['Experiment_time']}</p>", unsafe_allow_html=True)
            st.image(item["MMD_statistic_image"], caption="MMD_statistic_image", use_column_width=True)

def display_jobs_status_for_running_or_failed_jobs():
    """Display the running or failed jobs."""
    st.title("Running or Failed jobs")

    start_dt, end_dt = get_filters_for_runing_or_failed_jobs()
    jobs = fetch_uncompleted_jobs(start_dt, end_dt)

    if jobs.empty:
        st.info("No running or failed jobs found.")
        return

    display_status_dataframe(jobs)

def get_filters_for_runing_or_failed_jobs():
    """Get filters for fetching the failed or running jobs"""
    start_dt = components.add_start_date()
    end_dt = components.add_end_date()
    return start_dt, end_dt

def fetch_uncompleted_jobs(start_dt, end_dt):
    """Fetch uncompleted jobs and prepare the dataframe"""
    jobs = utils.fetch_uncompleted(start_dt, end_dt)
    if jobs:
        return pd.DataFrame(jobs).sort_values(by="Experiment_time", ascending=False)
    return pd.DataFrame()

def display_status_dataframe(jobs):
    """Display the status jobs dataframe with appropriate columns"""
    columns = ["Experiment_time", "Job_status", "Experiment_id"]
    st.dataframe(jobs[columns])

# Main function for the Streamlit dashboard
def main():
    """Main function for the Streamlit dashboard."""
    selected_tab = st.sidebar.radio("Select Tab", tabs)
    
    if selected_tab == "Job Status":
        display_jobs_status_for_running_or_failed_jobs()
    elif selected_tab == "Completed Jobs":
        display_completed_jobs()
    else:
        raise RuntimeError(f"Invalid tab {selected_tab}")

if __name__ == "__main__":
    main()
