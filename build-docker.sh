# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to build docker images for project
#
# Attributions:
# - https://pythonspeed.com/articles/faster-multi-stage-builds/ 
# - https://www.devdungeon.com/content/taking-command-line-arguments-bash

#!/bin/bash
set -Eeuo pipefail

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

source common.sh

# Setup ARM executables
docker run --rm --privileged docker/binfmt:820fdd95a9972a5308930a2bdfb8573dd4447ad3

if ! docker buildx use mybuilder; then
    docker buildx create --name mybuilder
    docker buildx use mybuilder
    docker buildx inspect --bootstrap
fi

# Pull the latest version of the image, in order to
# populate the build cache:
# Pipe || true to prevent failures during very first run on CI pipeline
docker pull $BUILD_STAGE_IMAGE || true
docker pull $RPI_IMAGE        || true

# Build the buld stage:
docker buildx build --platform linux/arm/v7 --load --target build-image --tag $BUILD_STAGE_IMAGE .

# Build the runtime stage, using cached build stage:
docker buildx build --platform linux/arm/v7 --load --target runtime-image --tag $RPI_IMAGE .

if [[ -v PUSH ]]; then
    docker push $BUILD_STAGE_IMAGE
    docker push $RPI_IMAGE
fi
