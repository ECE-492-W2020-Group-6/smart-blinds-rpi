# Date: Mar 6, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to run interactive process for docker image

# Get common definitions
source common.sh

# Run image in daemon mode
docker run -p 5000:5000 -it -d --name $CONTAINER_NAME $RPI_IMAGE
