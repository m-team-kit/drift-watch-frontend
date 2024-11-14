# Drift Detection Dashboard  

## Introduction 

    This repository contains a Streamlit dashboard for monitoring and visualizing drift detection in machine learning models. The 
    dashboard allows users to select different types of drift (feature drift, concept drift, or no drift) and visualize the detected 
    drift parametersover a specified time period.

## Usage

### 1. Configuration

    - In .streamlit folder, add your AUTH_TOKEN inside secrets.toml file, it is required to access the API's
        e.g. 
        
        AUTH_TOKEN = "YOUR ACCESS TOKEN"


### 2. Building the Docker Image

    Navigate to the frontend directory and run the following command to build the Docker image:
    
    cd frontend

    docker build -t drift_detection_image .


### 3. Running a Docker Container

    After building the Docker image, you can run a Docker container based on that image. Use the following command: 

    docker run -p 8000:8000 -p 8501:8501 drift_detection_image

### 4. 
    Go to http://0.0.0.0:8501 to access the streamlit dashboard

