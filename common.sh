# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script that contains common variables

#!/bin/bash
set -Eeuo pipefail

GH_PKG_ROOT=docker.pkg.github.com/ece-492-w2020-group-6/smart-blinds-rpi
BUILD_STAGE_IMAGE=$GH_PKG_ROOT/rpi:build-stage
RPI_IMAGE=$GH_PKG_ROOT/rpi:latest

# Enable host x86 machine to run ARM executables with QEMU
docker run --rm --privileged docker/binfmt:820fdd95a9972a5308930a2bdfb8573dd4447ad3

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
