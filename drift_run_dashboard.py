import os
import sys
# Get the parent directory of the current script
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to the Python path
sys.path.append(parent_dir)


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
from datetime import datetime
from datetime import datetime, time
from settings import Config
import base64
st.set_page_config(layout="wide")

def fetch_feature_drift_data(url, start_datetime, end_datetime):

    query = {
        "datetime": {"$gte": start_datetime, "$lte": end_datetime},        
        "data_drift.drift": True,
        "job_status" : "Completed"
    }


    # Send a GET request with the JSON payload
    response = requests.get(
        url,        
        json=query
    )

    df = pd.DataFrame()

    json_data = json.loads(response.text)

 
    data = []

    if len(json_data) != 0:
        for item in json_data:
            data_drift = item["data_drift"]["parameters"]
            p_value = data_drift.get('p_value', None)
            
            
            # Extract the encoded image data from the JSON response
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


            if p_value:
                data.append({
                "drift_run_id": item["id"],
                "Experiment_time": item["datetime"],
                "p_value": item["data_drift"]["parameters"]["p_value"],
                "data_drift": item["data_drift"]["drift"],
                "MMD_statistic_image" : MMD_statistic_image,
                "data_distribution_image": data_distribution_image
            })

        df = pd.DataFrame(data)

    return df

    

def fetch_concept_drift_data(url, start_datetime, end_datetime):

    df = pd.DataFrame()
    query = {
        "datetime": {"$gte": start_datetime, "$lte": end_datetime},
        "concept_drift.drift": True,        
        "job_status" : "Completed"
    }


    # Send a GET request with the JSON payload
    response = requests.get(
        url,        
        json=query
    )


    json_data = json.loads(response.text)

    data = []

    if len(json_data) != 0:
        for item in json_data:
            concept_drift = item["concept_drift"]["parameters"]
            message = concept_drift.get('message', None)

            
            if message:
                data.append({
                "drift_run_id": item["id"],
                "Experiment_time": item["datetime"],
                "message": item["concept_drift"]["parameters"]["message"],
                "concept_drift": item["concept_drift"]["drift"]
            })
                
            

        df = pd.DataFrame(data)        

    return df


def fetch_no_drift_data(url_nd, start_datetime, end_datetime):
    
    df = pd.DataFrame()
    
    query = {"datetime":
              {"$gte": start_datetime, "$lte": end_datetime}, 
              "concept_drift.drift": False, 
              "data_drift.drift": False,
              "job_status" : "Completed"}
    
    response = requests.get(url_nd, json=query)

    json_data = json.loads(response.text)
    
    data = []
    for item in json_data:
        concept_drift = item["data_drift"]["parameters"]
        p_value = concept_drift.get('p_value', None)
        
        # Extract the encoded image data from the JSON response
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


        if p_value:
            data.append({
            "drift_run_id": item["id"],
            "Experiment_time": item["datetime"],
            "p_value": item["data_drift"]["parameters"]["p_value"],
            "data_drift": item["data_drift"]["drift"],
            "MMD_statistic_image" : MMD_statistic_image,
            "data_distribution_image": data_distribution_image
        })        
     
    df = pd.DataFrame(data)

    return df

def fetch_jobs_by_status(url, start_datetime, end_datetime):

    df = pd.DataFrame()
    
    query = {"datetime": {"$gte": start_datetime, "$lte": end_datetime }}

    response = requests.get(url, json=query)

    if response.status_code == 200:
        data = response.json()
        
        if data:
            data = [
                {
                    "drift_run_id": job.get("id"),
                    "job_status": job.get("job_status", "No status found"),
                    "datetime": job.get("datetime", ""),
                }
                for job in data
            ]

        filtered_data = [job for job in data if job["job_status"].lower() == "running" or job["job_status"].lower() == "failed"]
        return filtered_data
    

def display_jobs_by_status():
    st.title(f"Running or Failed jobs")
        
    url = f"{Config.monitoring_url}/drift"

    # Select Start Date
    start_date = st.date_input("Select Start Date", min_value=datetime(2021, 1, 1), max_value=datetime(2025, 12, 31))

    # Select Start Time
    start_time = st.time_input("Select Start Time", value=time(0, 0, 0))

    # Combine the selected date and time
    start_datetime = datetime.combine(start_date, start_time)
    start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Select Start Date
    end_date = st.date_input("Select End Date", min_value=datetime(2021, 1, 1), max_value=datetime(2025, 12, 31))

    # Select Start Time
    end_time = st.time_input("Select End Time", value=time(23, 59, 59))

    # Combine the selected date and time
    end_datetime = datetime.combine(end_date, end_time)
    end_datetime = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    

    jobs = fetch_jobs_by_status(url, start_datetime, end_datetime)

    if jobs:
        df = pd.DataFrame(jobs)
        df = df.sort_values(by="datetime", ascending=False)
        st.dataframe(df[["job_status", "datetime"]])

def display_data():
    # Select Start Date
    start_date = st.date_input("Select Start Date", min_value=datetime(2021, 1, 1), max_value=datetime(2025, 12, 31))

    # Select Start Time
    start_time = st.time_input("Select Start Time", value=time(0, 0, 0))

    # Combine the selected date and time
    start_datetime = datetime.combine(start_date, start_time)
    start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Select Start Date
    end_date = st.date_input("Select End Date", min_value=datetime(2021, 1, 1), max_value=datetime(2025, 12, 31))

    # Select Start Time
    end_time = st.time_input("Select End Time", value=time(23, 59, 59))

    # Combine the selected date and time
    end_datetime = datetime.combine(end_date, end_time)
    end_datetime = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Sidebar for selecting drift type


    # Add a radio button with three options: "Feature Drift", "Concept Drift", and "None Selected"
    selected_option = st.sidebar.radio("Select Drift Type", ["Feature Drift", "Concept Drift", "No Drift Detected"])

    # Set feature_drift and concept_drift based on the selected option
    if selected_option == "Feature Drift":
        feature_drift = True
        concept_drift = False
    elif selected_option == "Concept Drift":
        feature_drift = False
        concept_drift = True
    else:
        # If "None Selected" or no option is selected, set both feature_drift and concept_drift to False
        feature_drift = False
        concept_drift = False


    if feature_drift:
        
        url = f"{Config.monitoring_url}/drift"

        df = fetch_feature_drift_data(url, start_datetime, end_datetime)
        
        if not df.empty:
            # Streamlit app for feature drift            
            fig, ax = plt.subplots(figsize=(8, 4))
        
            color = np.random.rand(3,)
            ax.scatter(df['Experiment_time'], df["p_value"], label="P_value", color='#FF0000')

            ax.set_xlabel("Experiment Date")
            ax.set_ylabel("P-Value")
            ax.set_title("Feature Drift over Time")
            ax.legend(title="Metrics", loc="upper left")
                # Rotate x-axis labels at a 45-degree angle
            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)
            
        # Display the image retrieved from the API
        for _, item in df.iloc[-5:,:].iterrows():
            
            st.write("\n\n\n\n\n\n")  # Add more newline characters for extra vertical space

            if item.get('data_distribution_image', None):
                # Center the title and the image            
                
                st.write("<p style='text-align:center; font-weight:bold; font-size:24px;'>Data Distribution Graph for: " + str(item['Experiment_time']) + "</p>", unsafe_allow_html=True)
                st.image(item['data_distribution_image'], caption='data_distribution_image', use_column_width=True)
            
            if item.get('MMD_statistic_image', None):
                st.write("<p style='text-align:center; font-weight:bold; font-size:24px;'>MMD_statistics Graph for " + str(item['Experiment_time']) + "</p>", unsafe_allow_html=True)
                st.image(item['MMD_statistic_image'], caption='MMD_statistic_image', use_column_width=True)
            
            
            
    elif concept_drift:        
        url = f"{Config.monitoring_url}/drift"
        df = fetch_concept_drift_data(url, start_datetime, end_datetime)        
        if not df.empty:
            st.dataframe(df)
        
    else:
        url_nd = f"{Config.monitoring_url}/drift"
        df = fetch_no_drift_data(url_nd, start_datetime, end_datetime)

        if not df.empty:
               fig, ax = plt.subplots(figsize=(8, 4))
               plt.scatter(df["Experiment_time"], df["p_value"], color='#FF0000')
               plt.xlabel("Experiment Date")
               plt.ylabel("P-Value")
               plt.title("No Drift Plot")
               ax.legend(title="P_VALUE", loc="upper left")
               # Rotate x-axis labels at a 45-degree angle
               plt.xticks(rotation=45, ha="right")
               
               st.pyplot(fig)
                    
        # Display the image retrieved from the API
        for _, item in df.iloc[-5:,:].iterrows():
            
            st.write("\n\n\n\n\n\n")  # Add more newline characters for extra vertical space

            if item.get('data_distribution_image', None):
                # Center the title and the image            
                
                st.write("<p style='text-align:center; font-weight:bold; font-size:24px;'>Data Distribution Graph for: " + str(item['Experiment_time']) + "</p>", unsafe_allow_html=True)
                st.image(item['data_distribution_image'], caption='data_distribution_image', use_column_width=True)
            
            if item.get('MMD_statistic_image', None):
                st.write("<p style='text-align:center; font-weight:bold; font-size:24px;'>MMD_statistics Graph for " + str(item['Experiment_time']) + "</p>", unsafe_allow_html=True)
                st.image(item['MMD_statistic_image'], caption='MMD_statistic_image', use_column_width=True)


def run_dashboard():
    tabs = ["Job Status", "Completed Jobs"]
    selected_tab = st.sidebar.radio("Select Tab", tabs)

    if selected_tab == "Completed Jobs":
        display_data()
    elif selected_tab == "Job Status":
        display_jobs_by_status()


if __name__ == '__main__':
    run_dashboard()