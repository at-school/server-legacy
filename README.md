# Server for at-school written in Python Flask.

### Features

* Facial recognition
* Basic structure of classes, messages.
* Websocket for connection between server and client.

### Steps to get the server running

* Activate virtual environemnt `source venv/bin/activate`
* Install packages `pip3 install -r requirements.txt`
* Last step: `python runserver.py`. :smile: :smile: :smile:

### Build server in Docker Container
*   First run `build -t server:latest .` to build the image.
*   After, run `stop $(docker ps -a -q)` to stop any running container.
*   Then, run `rm $(docker ps -a -q)` to remove any existing container.
*   Lastly, type `run -p 5000:5000 server:latest` to run the container. 
    *   Put in `-d` to make the container run in the background.
