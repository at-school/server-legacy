# -*- coding: utf-8 -*-
""" Manipulates data from Gmail API

This module uses the Gmail API to send and recieve information from a
users mailbox.

Example usage:
	example usage can be seen within the README or by running the test
	file::

		$ python3 test_mail
Todo:
	* Within the `unpack payload` add a parameter to be able to compress
	the data before being returned, in order to minimise space.
	* Be able to delete specfic messages/threads from users mailbox.

	* This module was created as a part of:
	https://github.com/at-school and its use within the project is
	documented at https://atschool.live/blog/post/00008 *

"""

import os
import base64
import dateutil.parser as parser
from email.mime.text import MIMEText
from app.controllers.email.MailLogging import debug
from app.controllers.email.authentication import auth
from bson.objectid import ObjectId
from app.database import db


class Gmail:

    def __init__(self, token='token', pushNotification=True):
        self.user_id = 'me'
        self.service = auth(token)

        if (pushNotification):
            self.enablePushNotication()

        debug.createLog()

    def enablePushNotication(self):
        request = {
            'labelIds': ['INBOX'],
            'topicName': 'projects/atschoolmail-217810/topics/atschool'
        }
        result = self.service.users().watch(userId=self.user_id, body=request).execute()

    def stopPushNotification(self):
        self.service.users().stop(userId="me")

    def getMessageData(self, messages, format=None, log=False):
        """ Return a list of message data in dictionary format
        Args:
                messages (list): The returned object from the
                `getMessages` function
        """
        messages = [
            self.service.users().messages().get(userId=self.user_id,
                                                id=message['id'],
                                                format=format).execute()
            for message in messages['messages']
        ]
        if log:
            debug.writeLog(format+' message' if format else 'messages',
                           messages)
        return messages

    def getPayload(self, messages, log=False):
        """ Returns a list of payload data from message data
        Args:
                messages (list): The returned object from the
                `getMessageData` function
        """
        payloads = []
        for message in messages:
            payload = message['payload']
            payload['id'] = message['id']
            payloads.append(payload)
        if log:
            debug.writeLog('payload', payloads)
        return payloads

    def decodeMSG(self, message):
        """ Decodes `message` paramater into utf-8
        Arg:
                message (string): base64 encoded string
        """
        msgString = base64.urlsafe_b64decode(message.encode('ASCII'))
        decoded = msgString.decode("utf-8")
        return decoded

    def unpackPayload(self, payloads, bodies=True,
                      types=['html', 'plain'], log=False, x=0, depth=0):
        """
        recurses through message parts until it find the types
        specified, then returns the decoded part and appends it to a
        list/dictionary of all messages parts

        Args:
                payloads (dictionary): The returned object from the
                `getPayload` function

                bodies (bool): True to collect html or plain text bodies
                from payload, false for simply headers

                types (:obj:`list` of :obj:`str`): types of bodies to be
                returned, either `html` or `plain`

                log (bool): True to log output to ./logs directory

                *DO NOT ALTER THE FOLLOWING PARAMETERS, THEY ARE REQUIRED
                FOR THE RECURSION*
                x (int): Specifies the index of the payloads
                depth (int): Specifies the Depth of recursion
        """
        messageParts = []
        plain = False
        plainText = ''
        for msg in payloads:
            parts = {}

            if bodies:
                type = msg['mimeType']
                # Plain text
                if type == 'text/plain' and 'plain' in types:
                    plainText = self.decodeMSG(msg['body']['data'])
                    if depth == 0:
                        parts['plain'] = plainText
                    else:
                        plain = True
                # Html
                elif type == 'text/html' and 'html' in types:
                    plain = False
                    body = self.decodeMSG(msg['body']['data'])
                    if depth > 0:
                        return {"html": body}
                    parts['html'] = body
                # Other
                elif type[10:] in ['mixed', 'alternative',
                                   'related', 'report']:
                    msgParts = msg['parts']
                    parts = self.unpackPayload(msgParts, bodies=True,
                                               types=types, x=x, depth=depth+1)
                    if depth > 0:
                        return parts
                # Attatchment
                elif type[:10] == 'application':
                    pass
            # Headers
            if depth == 0:
                header = msg['headers']
                for head in header:
                    name, value = head['name'], head['value']
                    if name == 'Date':
                        parts['dateTime'] = value
                    if name == 'Subject' or name == "subject":
                        parts['Subject'] = value
                    if name == 'From':

                        if '<' in value:
                            FROM, EMAIL = value.split('<')
                            parts['From'] = FROM[:-1]
                            parts['From-email'] = EMAIL[:-1]
                        else:
                            parts['From-email'] = value
            messageParts.append(parts)
            x += 1
            if depth == 0:
                parts["Id"] = msg["id"]
        if plain and depth > 0:
            plain = False
            return {"plain": plainText[:20]}
        return messageParts

    def getUserInfo(self):
        return self.service.users().labels().get(userId=self.user_id,
                                                 id="INBOX").execute()

    def getNewestEmail(self, historyId, historyTypes="messageAdded"):
        return self.service.users().history().list(
            userId="me", startHistoryId=historyId, historyTypes=historyTypes).execute()

    def getSingleEmail(self, mailId):
        return self.service.users().messages().get(
            userId="me", id=mailId).execute()

    def sendMessage(self, receiver, subject, content):
        """ Sends a messages from users mailbox """

        def createMessage():
            """ Creates a MIME fromat email message """
            message = MIMEText(content, "html")
            message['to'] = receiver
            message['from'] = "me"
            message['subject'] = subject
            return {'raw': base64.urlsafe_b64encode(
                message.as_bytes()).decode()}

        # create message base64 with MIMEText format
        createdMessage = createMessage()
        # sends message
        message = (self.service.users().messages().send(userId="me",
                                                        body=createdMessage).execute())


class GetMessages():

    def __init__(self, token='token'):
        self.service = auth(token)

    def list(self, maxResults=1, labelIds=["INBOX"]):
        """
        Returns a list of messages and thread Id's for n number
        of messages
        """
        msgList = self.service.users().messages().list(userId='me',
                                                       labelIds=labelIds, maxResults=maxResults).execute()

        return msgList

    def query(self, results=1, query=''):
        """
        Returns a list of messages and thread Id's for n number
        of messages that meet a specific query
        """
        return self.service.users().messages().list(userId='me',
                                                    q=query, maxResults=results).execute()
