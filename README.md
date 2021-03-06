![CD](https://github.com/ECE-492-W2020-Group-6/smart-blinds-rpi/workflows/CD/badge.svg)

# About

Smart Blinds. Runs on Python 3.

# Installing System Dependencies

`sudo apt-get update && apt-get install -y git build-essential libatlas3-base libgfortran5`

# Installing App Dependencies

To install production dependencies, (ie. no tests), run the following command:

`pip install requirements.txt`

However, there are several dependencies that are useful for developement (ex. testing and mocking libraries). So run this command instead of the earlier one if you intend to write/run unit tests as well as the application:

`pip install requirements-dev.txt`

# Adding Dependencies

Any dependencies that are used only for testing should be added to *requirements-dev.txt*.

All other dependencies should be added to *requirements.txt*.

