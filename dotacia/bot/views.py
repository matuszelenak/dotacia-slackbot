import json

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from bot.events import handle_event
from bot.commands import handle_command

SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)


class EventView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        print(json.dumps(slack_message, indent=4))

        if slack_message.get('token') != settings.SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message, status=status.HTTP_200_OK)

        if 'event' in slack_message:
            return handle_event(slack_message)

        return Response(status=status.HTTP_200_OK)


class CommandView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        print(json.dumps(slack_message, indent=4))

        if 'command' in slack_message:
            handle_command(slack_message)

        return Response(status=status.HTTP_200_OK)
