

def createMessageQuery(senderId, messageContent, chatroomId):
    """
    Arguments:
      - userInfo: a dictionary contains user info: username, 
                  email, firstname, lastname, accessLevel, password
    """

    return '''
        mutation addMessage {
            createMessage (arguments: { senderId: "%s", messageContent: "%s",
                                     chatroomId: "%s" } ) {
                Id
            }
        }
    ''' % (senderId, messageContent, chatroomId)
