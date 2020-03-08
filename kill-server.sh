# Date: Mar 7, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to run kill-server logs

# Get common definitions
source common.sh

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
