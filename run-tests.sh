# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to run unit tests 
#
# Attributions:
# - https://pythonspeed.com/articles/faster-multi-stage-builds/ 

# Source common definitions
source common.sh

# Run unit tests in container and exit
docker run --rm $RPI_IMAGE python3 -m pytest
