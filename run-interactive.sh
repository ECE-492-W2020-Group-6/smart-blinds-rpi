# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to run interactive process for docker image

# Get common definitions
source common.sh

# Run server if container doesn't exist
if ! docker container inspect $CONTAINER_NAME > /dev/null 2>&1; then
    ./run-server.sh
fi

# Execute shell in container
docker exec -it $CONTAINER_NAME /bin/bash
