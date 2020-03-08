# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script that contains common variables

#!/bin/bash
set -Eeuo pipefail

DH_PKG_REPO=ece492w2020group6/smart-blinds-rpi
PRE_BUILD_STAGE_IMAGE=$DH_PKG_REPO:pre-build-stage
BUILD_STAGE_IMAGE=$DH_PKG_REPO:build-stage
RPI_IMAGE=$DH_PKG_REPO:latest

CONTAINER_NAME=rpi-code

# Enable host x86 machine to run ARM executables with QEMU
docker run --rm --privileged docker/binfmt:820fdd95a9972a5308930a2bdfb8573dd4447ad3
