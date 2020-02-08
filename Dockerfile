# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: ARM based docker image to run SMART blinds rpi code
#
# Attributions for this file:
# - https://pythonspeed.com/articles/faster-multi-stage-builds/
# - https://pythonspeed.com/articles/multi-stage-docker-python/ 
# - https://blog.realkinetic.com/building-minimal-docker-containers-for-python-applications-37d0272c52f3

# Set base image
FROM arm32v7/python:3.8.1-slim-buster as base

# Stage 1: Create image which contains app dependencies
FROM base as build-image

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip3 install -r requirements-dev.txt

# Stage 2: Copy deps from build-image and copy source code into new image to run app
FROM base as runtime-image

COPY --from=build-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
COPY . .
