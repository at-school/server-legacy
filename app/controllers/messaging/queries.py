

def createMessageQuery(messageContent, chatroomId):
    """
    Arguments:
      - userInfo: a dictionary contains user info: username, 
                  email, firstname, lastname, accessLevel, password
    """

    return '''
        mutation addMessage {
            createMessage (arguments: { messageContent: "%s",
                                     chatroomId: "%s" } ) {
                Id
            }
        }
    ''' % (messageContent, chatroomId)
