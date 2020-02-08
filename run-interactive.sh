# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to run interactive process for docker image

#!/bin/bash

# Get common definitions
source common.sh

# Run image in daemon mode
docker run -it -d --name rpi-code $RPI_IMAGE

# Execute shell in container
docker exec -it rpi-code /bin/bash

# Cleanup container
docker stop rpi-code
docker rm rpi-code



