#  @ School Server #

[![License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/at-school/spa/license)
[![](https://img.shields.io/badge/Version-Beta%200.1.0-brightgreen.svg)](atschool.live)

> The server will only work on Linux/OS systems

## Features ##

* Facial recognition
* Basic structure of classes, messages.
* Websocket for connection between server and client.


### How to run:

1. run `python3 -m venv venv`
2. run `source venv/bin/activate`
3. run `pip3 install -r requirements.txt`
4. run `python3 runserver.py`

### For Windows, you need to do this before taking the steps above:
1. Install Ubuntu subsystem: https://docs.microsoft.com/en-us/windows/wsl/install-win10
2. sudo apt-get update
3. sudo apt-get install python3-pip
4. cd ../../mnt
5. Now you should be able to see the drives on Windows (e.g. C, D). You can navigate to the server file after and follow the instructions we have.

### Build server in Docker Container
*   First run `build -t server:latest .` to build the image.
*   After, run `stop $(docker ps -a -q)` to stop any running container.
*   Then, run `rm $(docker ps -a -q)` to remove any existing container.
*   Lastly, type `run -p 5000:5000 server:latest` to run the container.
    *   Put in `-d` to make the container run in the background.
