"""Entry point for the Streamlit dashboard."""

import pandas as pd
import streamlit as st
from app import components, utils
import matplotlib.pyplot as plt
import numpy as np



# Set the page layout to wide
st.set_page_config(layout="wide")

# Define the tabs for the dashboard
tabs = ["Job Status", "Completed Jobs"]


# Main function for the Streamlit dashboard
def main():
    """Main function for the Streamlit dashboard."""
    match st.sidebar.radio("Select Tab", tabs):
        case "Job Status":
            display_jobs_status()
        case "Completed Jobs":
            display_completed_jobs()
        case _tab:
            raise RuntimeError(f"Invalid tab {_tab}")


def display_jobs_status():
    """Display the running or failed jobs."""
    st.title("Running or Failed jobs")

    # Add the start and end date components
    start_dt = components.add_start_date()
    end_dt = components.add_end_date()

    # Fetch the uncompleted jobs based on the selected date and time
    jobs = utils.fetch_uncompleted(start_dt, end_dt)
    if not jobs:
        st.info("No running or failed jobs found.")
        return
    
    # Display the jobs in a DataFrame
    df = pd.DataFrame(jobs).sort_values(by="Experiment_time", ascending=False)
    columns = ["Experiment_time", "Job_status", "Experiment_id"]
    st.dataframe(df[columns])


# Define the drift filter options for the completed tab
drift_options = ["Feature Drift", "Concept Drift", "No Drift Detected"]


def display_completed_jobs():
    """Display the completed jobs and generate graphs based on their parameters / features"""
    st.title("Completed jobs")

    # Add the start and end date components
    start_dt = components.add_start_date()
    end_dt = components.add_end_date()

    # Set feature_drift and concept_drift for filtering
    data = st.sidebar.checkbox("Feature Drift", value=True)
    concept = st.sidebar.checkbox("Concept Drift", value=True)

    # Fetch the completed jobs based on the selected date and time
    jobs = utils.fetch_drifts(start_dt, end_dt, data, concept)

    if not jobs:
        st.info("No running or failed jobs found.")
        return
    
    # converting to dataframe
    jobs = pd.DataFrame(jobs)

    #renaming
    data_drift = data 
    concept_drift = concept
    
    no_drift = False  # Default value
    
    # if there is no drift, set this variable to true
    if not data_drift and not concept_drift:
        no_drift = True

   
    # Display the jobs in a DataFrame
    
    df = jobs.sort_values(by="Experiment_time", ascending=False)

    # Adjusting columns to display and graph title based upon type of drift
    if concept_drift and data_drift:
        columns = ["drift_run_id", "Experiment_time", "concept_drift", "data_drift", "concept_drift_parameters", "data_drift_parameters"]      
        graph_title = "both concept and data drift over time"

    elif concept_drift:              
        graph_title = "concept drift over time"       
        columns = ["drift_run_id", "Experiment_time", "concept_drift", "concept_drift_parameters"]      
            
    elif data_drift:            
        graph_title = "data drift over time"
        columns = ["drift_run_id", "Experiment_time", "data_drift", "data_drift_parameters"]      

    elif no_drift:
        graph_title = "no drift over time"
        columns = ["drift_run_id", "Experiment_time", "concept_drift", "data_drift", "concept_drift_parameters", "data_drift_parameters"]      
        

    # display dataframe before graphs
    st.dataframe(df[columns])
    

    # Collect features to display in graphs

    feature_drift_list = []
    features = set()
    for index, item in df.iterrows():
        feature_drift_dict = {}            
        
        for key, value in item['data_drift_parameters'].items():
            if key != 'data_distribution_image' and key != 'MMD_statistic_image':
                feature_drift_dict[key] = value
                features.add(key)
    
    
        for key, value in item['concept_drift_parameters'].items():
            if key != 'data_distribution_image' and key != 'MMD_statistic_image':
                feature_drift_dict[key] = value
                features.add(key)

        feature_drift_list.append(feature_drift_dict)

    # generate graphs for selected features    
    if not df.empty:
        selected_features = st.sidebar.multiselect("Select Features", features, default=features)

        if selected_features:
            fig, ax = plt.subplots(figsize=(15, 8))
            for feature in selected_features:                    
                    color = np.random.rand(3,)
                    ax.scatter(df['Experiment_time'], [item.get(feature, None) for item in feature_drift_list], label=feature, color=color)

            ax.set_xlabel("Experiment Date")
            ax.set_ylabel("Feature Values")

            ax.set_title(f"{graph_title}")
            ax.legend(title="Features", loc="upper left")
                # Rotate x-axis labels at a 45-degree angle
            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)
        else:
            st.warning("Please select at least one feature.")

                

    # Display the image retrieved from the API, if exists
    for index, item in df.iloc[-5:,:].iterrows():
        if index == 0:
            if item.get('data_distribution_image', None):
                st.write("<p style='text-align:center; font-weight:bold; font-size:24px;'>Last 5 experiments graphs : </p>", unsafe_allow_html=True)
        
        st.write("\n\n\n\n\n\n")  # Add more newline characters for extra vertical space

        if item.get('data_distribution_image', None):
            # Center the title and the image            
            
            st.write("<p style='text-align:center; font-weight:bold; font-size:16px;'>Data Distribution Graph for: " + str(item['Experiment_time']) + "</p>", unsafe_allow_html=True)
            st.image(item['data_distribution_image'], caption='data_distribution_image', use_column_width=True)
        
        if item.get('MMD_statistic_image', None):
            st.write("<p style='text-align:center; font-weight:bold; font-size:16px;'>MMD_statistics Graph for " + str(item['Experiment_time']) + "</p>", unsafe_allow_html=True)
            st.image(item['MMD_statistic_image'], caption='MMD_statistic_image', use_column_width=True)
        


if __name__ == "__main__":
    main()
