import json


def loginQuery(username):
    return '''
        query login {
            user(arguments: { username: "%s" } ) {
                Id
                firstname
                lastname
                password
                accessLevel
                username
                avatar
            }
        }
    ''' % username


def registerQuery(username, firstname, lastname, email, password, accessLevel, gender, dob, phone):
    """
    Arguments:
      - userInfo: a dictionary contains user info: username, 
                  email, firstname, lastname, accessLevel, password, dob, gender, phone
    """

    return '''
        mutation addUser {
            createUser (arguments: { username: "%s", firstname: "%s",
                                     lastname: "%s", password: "%s",
                                     accessLevel: %i, email: "%s", gender: "%s", dob: "%s", phone: "%s" } ) {
                username
            }
        }
    ''' % (username, firstname, lastname, password, accessLevel, email, gender, dob, phone)
