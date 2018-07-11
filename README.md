# Server for at-school written in Python Flask.

### Steps to get the server running
*   Make sure have the public key and private key inside a folder called `keys` in the main directory.
    *   If don't have, type `ssh-keygen -t rsa -b 4096` inside the commandline to generate two of the keys.
*   Include the database:
    *   `flask db init`
    *   `flask db migrate`
    *   `flask db upgrade`
* Include the trained model for emojifier. It lives in `at-school-server/app/controllers/emojifier/emojifier_LSTM.h5`.
* Also include the GloVE Embeddings. It lives in `at-school-server/glove.6B.200.txt`.
*   Initialize the timetable:
    *   Run `flask shell` to get into the flask context.
    *   Invoke `emojifier_setup` to setup the database for word embeddings.
    *   Invoke `schedule_setup` to setup the schedule.
    *   Invoke `falcuty_setup` to setup the falcuty of the school.
* Last step: `python runserver.py`. :smile: :smile: :smile:

*If cannot have the model, remove everything that has emofjier in `at-school-server/runserver.py` and `at-school-server/app/__init__.py`.*

### Build server in Docker Container
*   First run `build -t server:latest .` to build the image.
*   After, run `stop $(docker ps -a -q)` to stop any running container.
*   Then, run `rm $(docker ps -a -q)` to remove any existing container.
*   Lastly, type `run -p 5000:5000 server:latest` to run the container. 
    *   Put in `-d` to make the container run in the background.
