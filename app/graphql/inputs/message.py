import graphene

class MessageInput(graphene.InputObjectType):
    chatroomId = graphene.ID()
    messageContent = graphene.String()
    senderId = graphene.ID()
    senderAvatar = graphene.String()