# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to build docker images for project
#
# Attributions:
# - https://pythonspeed.com/articles/faster-multi-stage-builds/ 
# - https://www.devdungeon.com/content/taking-command-line-arguments-bash

#!/bin/bash
set -Eeuo pipefail

# Parse args
for arg in "$@"
do
    if [ "$arg" = "--push" ]; then
        PUSH=true
    fi

    if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
        echo "TODO: HELP"
        exit
    fi
done

# Source common definitions
source common.sh

# Create and set buildkit builder instance
if ! docker buildx use mybuilder; then
    docker buildx create --name mybuilder
    docker buildx use mybuilder
    docker buildx inspect --bootstrap
fi

# Pull the latest version of the image, in order to populate the build cache
# Pipe || true to prevent failures when image doesn't exist in registry
docker pull $BUILD_STAGE_IMAGE || true
docker pull $RPI_IMAGE || true

# Build the buld stage image:
docker buildx build --platform linux/arm/v7 --load --target build-image --tag $BUILD_STAGE_IMAGE .

# Build the runtime stage image:
docker buildx build --platform linux/arm/v7 --load --target runtime-image --tag $RPI_IMAGE .

# Push image to registry if cli argument set
if [[ -v PUSH ]]; then
    docker push $BUILD_STAGE_IMAGE
    docker push $RPI_IMAGE
fi
