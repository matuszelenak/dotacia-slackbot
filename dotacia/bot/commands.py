from django.conf import settings
from slack import WebClient

from bot.constants import *
from bot.actions import *


def parse_dotacia_arguments(text):
    text = text.lower().strip()

    if not text:
        return {
            'action': print_help
        }

    m = NUMBER_GIVE_TEMPLATE.match(text)
    if m:
        return {
            'action': give_number,
            'action_args': {
                'amount': m.group('amount') or 1
            }
        }

    m = NUMBER_REGISTER_TEMPLATE.match(text)
    if m:
        number = m.group('number')
        priority = m.group('priority') or ISIC.MAX_PRIORITY
        return {
            'action': register_number,
            'action_args': {
                'number': number,
                'priority': priority
            }
        }

    m = NUMBER_SET_PRIORITY_TEMPLATE.match(text)
    if m:
        return {
            'action': set_number_priority,
            'action_args': {
                'priority': m.group('priority')
            }
        }

    m = NUMBER_ENABLE_TEMPLATE.match(text)
    if m:
        return {
            'action': enable_number
        }

    m = NUMBER_DISABLE_TEMPLATE.match(text)
    if m:
        return {
            'action': disable_number
        }

    m = NUMBER_USE_TEMPLATE.match(text)
    if m:
        return {
            'action': use_number
        }

    return {}


def handle_command(payload):
    if payload['command'] == COMMAND_DOTACIA:
        args = parse_dotacia_arguments(payload['text'])
        action_args = args.get('action_args', {})
        action_args.update({'slack_user_id': payload['user_id']})
        print(args)
        if args:
            reply = args['action'](**action_args)
        else:
            reply = print_help()
    else:
        reply = 'Unrecognized command'

    if reply:
        client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)
        response = client.chat_postEphemeral(
            channel=payload['channel_id'],
            text=reply,
            user=payload['user_id']
        )
