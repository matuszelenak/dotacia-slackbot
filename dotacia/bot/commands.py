import re

from django.conf import settings
from slack import WebClient

from bot.actions import *

DOTACIA_SUBCOMMANDS = [
    {
        'description': 'Gives you ISIC number and notes its usage',
        'example': '/dotacia give',
        'regex': re.compile('^give$'),
        'action': give_number,
    },
    {
        'description': 'Gives you specified amount of ISIC numbers and notes their usage',
        'example': '/dotacia give 5',
        'regex': re.compile('^give +(?P<amount>[0-9]+)$'),
        'action': give_number,
    },
    {
        'description': 'Registers an ISIC number and binds it to your profile',
        'example': '/dotacia register 36086128512851296',
        'regex': re.compile('^register +(?P<number>[0-9]+)$'),
        'action': register_number,
    },
    {
        'description': 'Sets the priority of your ISIC number (high, medium, low)',
        'example': '/dotacia priority high',
        'regex': re.compile('^priority +(?P<priority>{})$'.format('|'.join(desc for _, desc in ISIC.PRIORITY_CHOICES))),
        'action': set_number_priority,
    },
    {
        'description': 'Removes your ISIC number from the shared pool',
        'example': '/dotacia disable',
        'regex': re.compile('^disable$'),
        'action': disable_number,
    },
    {
        'description': 'Includes your ISIC number into the shared pool',
        'example': '/dotacia enable',
        'regex': re.compile('^enable$'),
        'action': enable_number,
    },
    {
        'description': 'Includes your ISIC number into the shared pool',
        'example': '/dotacia use',
        'regex': re.compile('^use$'),
        'action': use_number,
    },
]

DOTACIA_HELP_MESSAGE = '*Dotacia command usage:* \n' + '\n\n'.join(
    f'{subcommand["description"]}\nExample: _{subcommand["example"]}_' for subcommand in DOTACIA_SUBCOMMANDS
)


def handle_command(payload):
    reply = None
    if payload['command'] == '/dotacia':
        used_correctly = False
        for subcommand in DOTACIA_SUBCOMMANDS:
            m = subcommand['regex'].match(payload['text'].lower())
            if m:
                action_args = m.groupdict()
                action_args.update({'slack_user_id': payload['user_id']})
                reply = subcommand['action'](**action_args)
                used_correctly = True
                break
        if not used_correctly:
            reply = DOTACIA_HELP_MESSAGE
    else:
        reply = 'Unrecognized command'

    if reply:
        sender = SlackUser.objects.for_user_id(payload['user_id'])
        client = WebClient(token=settings.SLACK_BOT_USER_TOKEN)
        message_kwargs = dict(channel=payload['channel_id'], text=reply)
        if sender.slack_channel_id == payload['channel_id']:
            client.chat_postMessage(**message_kwargs)
        else:
            client.chat_postEphemeral(user=payload['user_id'], **message_kwargs)
