# Date: Feb 8, 2020
# Author: Ishaat Chowdhury
# Contents: bash script to run unit tests 
#
# Attributions:
# - https://pythonspeed.com/articles/faster-multi-stage-builds/ 

#!/bin/bash
set -Eeuo pipefail

GH_PKG_ROOT=docker.pkg.github.com/ece-492-w2020-group-6/smart-blinds-rpi

docker run --rm $GH_PKG_ROOT/rpi:latest python3 -m pytest
