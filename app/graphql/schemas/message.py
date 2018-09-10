import graphene

class MessageSchema(graphene.ObjectType):
    _id = graphene.ID()
    senderId = graphene.ID()
    senderAvatar = graphene.String()
    messageContent = graphene.String()
    timestamp = graphene.DateTime()
    chatroomId = graphene.ID()