# ================================== BUILDER ===================================
ARG  PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION} as build

# Environments to reduce size of docker image
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONFAULTHANDLER=true
ENV PYTHONUNBUFFERED=true
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=true
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

# Install system updates and tools
RUN apt-get update 
RUN python -m pip install --upgrade pip

# Add workdir and user non root user
WORKDIR /srv
RUN useradd -m sid

# ================================= PRODUCTION =================================
FROM build AS production
USER root

# Copy and install production requirements
COPY --chown=sid:sid requirements.txt /srv
RUN python -m pip install -r requirements.txt

# Copy the rest of the application
COPY --chown=sid:sid drift_run_dashboard.py /srv

# Change to non root user and expose port
USER sid
EXPOSE 8000
EXPOSE 8501

# Define entrypoint and default command
# ENTRYPOINT [ "python" ]
CMD [ "streamlit", "run", "drift_run_dashboard.py" ]

# ================================= DEVELOPMENT ================================
FROM production AS development
USER root

# Copy and install development requirements
COPY --chown=sid:sid requirements-dev.txt /srv
RUN python -m pip install -r requirements-dev.txt

# Change to non root user and expose port
USER sid
EXPOSE 8501
EXPOSE 5678
EXPOSE 8000

# Define entrypoint and default command
# ENTRYPOINT ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client" ]
# ENTRYPOINT [ "python" ]
CMD [ "streamlit", "run", "drift_run_dashboard.py" ]
