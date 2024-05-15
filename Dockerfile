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

# Copy and install production requirements
COPY --chown=sid:sid app /srv/app
COPY --chown=sid:sid requirements.txt /srv
COPY --chown=sid:sid dashboard.py /srv
RUN python -m pip install -r requirements.txt

# ================================= PRODUCTION =================================
FROM build AS production
USER root

# Change to non root user and expose port
USER sid
EXPOSE 8501

# Define entrypoint and default command
ENTRYPOINT [ "python", "-m", "streamlit" ]
CMD [ "run", "dashboard.py" ]

# ================================= DEVELOPMENT ================================
FROM build AS development
USER root

# Copy and install debugger requirements
RUN pip install debugpy

# Change to non root user and expose port
USER sid
EXPOSE 8501
EXPOSE 5678

# Define entrypoint and default command
ENTRYPOINT ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "streamlit" ]
CMD [ "run", "dashboard.py" ]
