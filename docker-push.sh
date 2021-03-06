# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to push docker images to GitHub Packages

# Source common definitions
source common.sh

# Push images to registry
docker push $PRE_BUILD_STAGE_IMAGE
docker push $BUILD_STAGE_IMAGE
docker push $RPI_IMAGE
