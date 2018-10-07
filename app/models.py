from hashlib import md5

from werkzeug.security import check_password_hash, generate_password_hash


class User():

    def __init__(self, username, firstname, lastname, email, accessLevel, gender, dob, **kwargs):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.accessLevel = accessLevel
        self.avatar = 'https://www.gravatar.com/avatar/{}?d=identicon&s=256'.format(
            md5(self.username.lower().encode('utf-8')).hexdigest())
        self.password = ""
        self.gender = gender,
        self.dob = dob

    def get_default_avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    def setPassword(self, password):
        """Runs the passwords through a hash and appends."""
        self.password = generate_password_hash(str(password))

    @classmethod
    def findUsers(self, id=None, username=None, firstname=None):
        if (id):
            # search user by id here
            pass
        elif (username):
            # search user by name here
            return Database.db.users.find({"username": username})
        elif (firstname):
            pass

        return None

    @classmethod
    def checkPassword(self, password, password1):
        """Checks a password against the hash."""
        return check_password_hash(password, password1)
