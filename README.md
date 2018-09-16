#  @ School Server #

[![License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/at-school/spa/license)
[![](https://img.shields.io/badge/Version-Beta%200.1.0-brightgreen.svg)](atschool.live)

**Future Plans:**
* sdasf
* asdfdasf
* asdfafds

Welcome to **@ School**'s single web app **Beta**!

This will be updated every time a new beta is released. It is here to show core functionalities, progress and our adherence to time line for anyone wanting to support or contribute to the project. If you are interested in supporting the project, please contact one of our [team members]('https://atschool.live/about/team').

If you are interested in viewing our weekly progress please take a look at our weekly [blog posts](https://atschool.live/blog).
## Features ##

### How To Run

* Activate virtual environemnt `source venv/bin/activate`
* Install packages `pip3 install -r requirements.txt`
* Last step: `flask run --host=0.0.0.0`. :smile: :smile: :smile:

### Build server in Docker Container
*   First run `build -t server:latest .` to build the image.
*   After, run `stop $(docker ps -a -q)` to stop any running container.
*   Then, run `rm $(docker ps -a -q)` to remove any existing container.
*   Lastly, type `run -p 5000:5000 server:latest` to run the container. 
    *   Put in `-d` to make the container run in the background.
