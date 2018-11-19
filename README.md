#  @ School Server #

[![License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/at-school/spa/license)
[![](https://img.shields.io/badge/Version-Beta%200.1.0-brightgreen.svg)](atschool.live)


## Features ##

* Facial recognition
* Basic structure of classes, messages.
* Websocket for connection between server and client.


### How to run:

1. run `python3 -m venv venv`
2. run `source venv/bin/activate`
3. run `pip3 install -r requirements.txt`
4. run `flask run --host=0.0.0.0`

### Build server in Docker Container
*   First run `build -t server:latest .` to build the image.
*   After, run `stop $(docker ps -a -q)` to stop any running container.
*   Then, run `rm $(docker ps -a -q)` to remove any existing container.
*   Lastly, type `run -p 5000:5000 server:latest` to run the container.
    *   Put in `-d` to make the container run in the background.
