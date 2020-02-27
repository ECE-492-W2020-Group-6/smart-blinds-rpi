# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: ARM based docker image to run SMART blinds rpi code
#
# Attributions for this file:
# - https://pythonspeed.com/articles/faster-multi-stage-builds/
# - https://pythonspeed.com/articles/multi-stage-docker-python/ 
# - https://blog.realkinetic.com/building-minimal-docker-containers-for-python-applications-37d0272c52f3

# Set base image
FROM arm32v7/python:3.7-slim-buster as base

# Stage 1: Create image which contains app dependencies
FROM base as build-image

# Install apt packages
RUN apt-get update -y && \ 
    apt-get install -y git build-essential libatlas3-base libgfortran5 

# Create virtualenv
RUN python -m venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip3 install --upgrade pip

# Copy requirements
COPY requirements.txt .
COPY requirements-dev.txt .

# Install requirements, uses piwheels (https://www.piwheels.hostedpi.com/) as an alternative package repo
RUN pip3 install -r requirements-dev.txt --extra-index-url https://www.piwheels.org/simple

# Stage 2: Create image to run app
FROM base as runtime-image

# Copy virtualenv from build-image
COPY --from=build-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code to container
WORKDIR /src
COPY . .
