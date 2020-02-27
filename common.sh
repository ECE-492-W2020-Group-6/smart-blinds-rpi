# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script that contains common variables

#!/bin/bash
set -Eeuo pipefail

GH_PKG_ROOT=docker.pkg.github.com/ece-492-w2020-group-6/smart-blinds-rpi
PRE_BUILD_STAGE_IMAGE=$GH_PKG_ROOT/rpi:pre-build-stage
BUILD_STAGE_IMAGE=$GH_PKG_ROOT/rpi:build-stage
RPI_IMAGE=$GH_PKG_ROOT/rpi:latest

# Enable host x86 machine to run ARM executables with QEMU
docker run --rm --privileged docker/binfmt:820fdd95a9972a5308930a2bdfb8573dd4447ad3
