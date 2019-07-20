from rest_framework import status
from rest_framework.response import Response


EVENT_MESSAGE = 'message'
EVENT_MENTION = 'app_mention'

EVENT_TYPES = (
    'message',
    'app_mention',
)


def handle_message(message):
    pass


def handle_event(message):
    event = message['event']
    if event['type'] == EVENT_MESSAGE:
        print(event)

    return Response(data={}, status=status.HTTP_200_OK)
