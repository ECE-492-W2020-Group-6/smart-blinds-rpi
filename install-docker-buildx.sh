# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script that installs and configures docker-buildx

#!/bin/bash
set -Eeuo pipefail

# Install docker buildx
if ! docker buildx > /dev/null 2>&1; then
    mkdir -p ~/.docker/cli-plugins/
    wget -O ~/.docker/cli-plugins/docker-buildx  https://github.com/docker/buildx/releases/download/v0.3.1/buildx-v0.3.1.linux-amd64
    chmod a+x ~/.docker/cli-plugins/docker-buildx

    export DOCKER_CLI_EXPERIMENTAL=enabled   

    sudo systemctl restart docker

    if ! docker buildx > /dev/null 2>&1; then
        echo "docker buildx installation failed"
        docker info
        exit 1
    fi
fi
